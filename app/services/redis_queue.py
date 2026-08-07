"""Redis FIFO queue for non-blocking portfolio simulations."""

import asyncio
import contextlib
import json
import uuid

from redis.asyncio import Redis
from redis.exceptions import RedisError


class QueueUnavailable(RuntimeError):
    pass


class RedisJobQueue:
    queue_key = "aurawealth:simulation:queue"
    job_prefix = "aurawealth:simulation:job:"

    def __init__(self, redis_url: str) -> None:
        self.client = Redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=0.5)
        self.worker_task: asyncio.Task | None = None

    async def start(self) -> None:
        if self.worker_task is None or self.worker_task.done():
            self.worker_task = asyncio.create_task(self._worker_loop(), name="aurawealth-redis-worker")

    async def stop(self) -> None:
        if self.worker_task:
            self.worker_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.worker_task
        await self.client.aclose()

    async def enqueue_batch(self, payloads: list[dict]) -> list[dict]:
        queued_jobs = []
        try:
            for sequence, payload in enumerate(payloads, start=1):
                job_id = f"job_{uuid.uuid4().hex[:8]}"
                job_key = f"{self.job_prefix}{job_id}"
                await self.client.hset(job_key, mapping={
                    "status": "queued",
                    "progress": "0",
                    "submitted_order": str(sequence),
                    "payload": json.dumps(payload),
                })
                await self.client.expire(job_key, 86400)
                await self.client.rpush(self.queue_key, job_id)
                queued_jobs.append({"job_id": job_id, "status": "queued", "submitted_order": sequence})
        except (RedisError, OSError) as error:
            raise QueueUnavailable("Redis queue is unavailable.") from error
        return queued_jobs

    async def get_job(self, job_id: str) -> dict | None:
        try:
            job = await self.client.hgetall(f"{self.job_prefix}{job_id}")
        except (RedisError, OSError) as error:
            raise QueueUnavailable("Redis queue is unavailable.") from error
        if not job:
            return None
        return {
            "job_id": job_id,
            "status": job["status"],
            "progress": int(job["progress"]),
            "submitted_order": int(job["submitted_order"]),
            "result": float(job["result"]) if "result" in job else None,
        }

    async def _worker_loop(self) -> None:
        while True:
            try:
                item = await self.client.blpop(self.queue_key, timeout=1)
                if item is None:
                    continue
                _, job_id = item
                await self._process(job_id)
            except asyncio.CancelledError:
                raise
            except (RedisError, OSError):
                await asyncio.sleep(1)

    async def _process(self, job_id: str) -> None:
        job_key = f"{self.job_prefix}{job_id}"
        job = await self.client.hgetall(job_key)
        if not job:
            return
        payload = json.loads(job["payload"])
        await self.client.hset(job_key, mapping={"status": "processing", "progress": "50"})
        await asyncio.sleep(1)
        projected = payload["initial_capital"] * (1.08 ** payload["horizon_years"])
        await self.client.hset(job_key, mapping={
            "status": "completed",
            "progress": "100",
            "result": str(round(projected, 2)),
        })
