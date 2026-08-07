import pytest

from app.services.cache import SearchCache


@pytest.mark.asyncio
async def test_redis_cache_returns_a_hit_and_ttl(fake_redis):
    cache = SearchCache("redis://unused")
    cache.client = fake_redis
    await cache.set("tax", [{"id": "doc_1"}])
    cached, backend = await cache.get("tax")
    assert cached == [{"id": "doc_1"}]
    assert backend == "redis"
    assert await fake_redis.ttl(cache._key("tax")) > 0
    await cache.close()
