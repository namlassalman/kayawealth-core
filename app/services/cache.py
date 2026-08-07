"""Redis-backed cache with a short-lived in-memory resilience fallback."""

import hashlib
import json
import time
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError


class SearchCache:
    def __init__(self, redis_url: str, ttl_seconds: int = 60) -> None:
        self.client = Redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=0.5)
        self.ttl_seconds = ttl_seconds
        self._fallback: dict[str, tuple[float, list[dict[str, Any]]]] = {}

    @staticmethod
    def _key(query: str) -> str:
        digest = hashlib.sha256(query.strip().lower().encode()).hexdigest()
        return f"aurawealth:search:{digest}"

    async def get(self, query: str) -> tuple[list[dict[str, Any]] | None, str]:
        key = self._key(query)
        try:
            value = await self.client.get(key)
            return (json.loads(value), "redis") if value else (None, "redis")
        except (RedisError, OSError):
            fallback = self._fallback.get(key)
            if fallback and fallback[0] > time.monotonic():
                return fallback[1], "in_memory_fallback"
            self._fallback.pop(key, None)
            return None, "in_memory_fallback"

    async def set(self, query: str, value: list[dict[str, Any]]) -> str:
        key = self._key(query)
        try:
            await self.client.set(key, json.dumps(value), ex=self.ttl_seconds)
            return "redis"
        except (RedisError, OSError):
            self._fallback[key] = (time.monotonic() + self.ttl_seconds, value)
            return "in_memory_fallback"

    async def close(self) -> None:
        await self.client.aclose()
