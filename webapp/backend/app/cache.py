"""Redis cache helpers for API responses.

A thin wrapper around redis-py so callers can cache and expire JSON
payloads. Redis unavailability is handled gracefully: on any connection
error the cache degrades to a no-op (cache miss, write silently skipped)
so the API keeps working without the cache.
"""

import json
import logging
from typing import Any

import redis

from app.config import settings

logger = logging.getLogger(__name__)

_client: redis.Redis | None = None

SEARCH_PREFIX = "search:"
SEARCH_TTL = 60  # seconds — short TTL keeps results reasonably fresh


def _redis() -> redis.Redis | None:
    global _client
    if _client is None:
        try:
            _client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
            _client.ping()
        except redis.RedisError:
            logger.warning("Redis unavailable; caching disabled", exc_info=True)
            _client = None
    return _client


def get_json(key: str) -> Any | None:
    """Return the cached JSON value for a key, or None on miss/error."""
    client = _redis()
    if client is None:
        return None
    try:
        raw = client.get(key)
        return json.loads(raw) if raw is not None else None
    except (redis.RedisError, json.JSONDecodeError):
        return None


def set_json(key: str, value: Any, ttl: int = SEARCH_TTL) -> None:
    """Cache a JSON-serialisable value under a key with a TTL (seconds)."""
    client = _redis()
    if client is None:
        return
    try:
        client.set(key, json.dumps(value, default=str), ex=ttl)
    except redis.RedisError:
        logger.warning("Redis set failed for %s", key, exc_info=True)


# Search-specific cache functions (compatible with mobile backend)
def search_cache_get(q: str, category: str | None) -> list | None:
    key = f"{SEARCH_PREFIX}{q}|{category or ''}"
    return get_json(key)


def search_cache_set(q: str, category: str | None, payload: list) -> None:
    key = f"{SEARCH_PREFIX}{q}|{category or ''}"
    set_json(key, payload)


def delete_prefix(prefix: str) -> int:
    """Delete all keys starting with a prefix. Returns number deleted."""
    client = _redis()
    if client is None:
        return 0
    try:
        keys = list(client.scan_iter(match=f"{prefix}*"))
        return client.delete(*keys) if keys else 0
    except redis.RedisError:
        return 0


def clear_search_cache() -> int:
    """Invalidate all cached search responses."""
    return delete_prefix(SEARCH_PREFIX)