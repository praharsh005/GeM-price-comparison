from app import cache


def test_cache_roundtrip():
    cache.search_cache_set("test-query", None, [{"id": 1, "name": "x"}])
    assert cache.search_cache_get("test-query", None) == [{"id": 1, "name": "x"}]
    cache.search_cache_set("test-query", None, None)


def test_cache_miss_returns_none():
    assert cache.search_cache_get("zzz-no-such-key", None) is None


def test_cache_graceful_when_redis_down(monkeypatch):
    monkeypatch.setattr(cache, "_client", None)

    def boom(*args, **kwargs):
        raise cache.redis.RedisError("connection refused")

    monkeypatch.setattr(cache.redis.Redis, "ping", boom)
    assert cache.search_cache_get("anything", None) is None
    cache.search_cache_set("anything", None, [])  # must not raise
