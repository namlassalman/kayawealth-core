import pytest

from app.services.redis_queue import RedisJobQueue


@pytest.mark.asyncio
async def test_redis_queue_preserves_submission_order(fake_redis):
    queue = RedisJobQueue("redis://unused")
    queue.client = fake_redis
    jobs = await queue.enqueue_batch([
        {"portfolio_name": "A", "initial_capital": 1000.0, "horizon_years": 1},
        {"portfolio_name": "B", "initial_capital": 2000.0, "horizon_years": 1},
    ])
    assert [job["submitted_order"] for job in jobs] == [1, 2]
    assert await fake_redis.lrange(queue.queue_key, 0, -1) == [job["job_id"] for job in jobs]
    await queue.stop()
