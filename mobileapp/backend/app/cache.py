import json

import redis

from app.config import REDIS_URL, SEARCH_CACHE_TTL_SECONDS

_client: redis.Redis | None = None


def _get_client() -> redis.Redis | None:
    global _client
    if _client is None:
        try:
            _client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
            _client.ping()
        except redis.RedisError:
            _client = None
    return _client


def cache_get(key: str) -> str | None:
    client = _get_client()
    if client is None:
        return None
    try:
        return client.get(key)
    except redis.RedisError:
        return None


def cache_set(key: str, value: str, ttl: int = SEARCH_CACHE_TTL_SECONDS) -> None:
    client = _get_client()
    if client is None:
        return
    try:
        client.set(key, value, ex=ttl)
    except redis.RedisError:
        pass


def search_cache_get(q: str, category: str | None) -> list | None:
    key = f"search:{q}|{category or ''}"
    cached = cache_get(key)
    if cached is None:
        return None
    try:
        return json.loads(cached)
    except (json.JSONDecodeError, TypeError):
        return None


def search_cache_set(q: str, category: str | None, payload: list) -> None:
    key = f"search:{q}|{category or ''}"
    cache_set(key, json.dumps(payload, ensure_ascii=False))