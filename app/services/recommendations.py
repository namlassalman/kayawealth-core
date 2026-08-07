"""Persisted human-review records for portfolio-change recommendations."""

from datetime import datetime, timezone
import uuid

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.models import JobStatus, RecommendationRecord


class RecommendationUnavailable(RuntimeError):
    pass


class RecommendationStore:
    key_prefix = "aurawealth:recommendation:"

    def __init__(self, redis_url: str) -> None:
        self.client = Redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=0.5)

    async def create(self, user_query: str, final_report: str) -> RecommendationRecord:
        record = RecommendationRecord(
            recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
            user_query=user_query,
            final_report=final_report,
            status=JobStatus.PENDING_REVIEW,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        try:
            await self.client.hset(self._key(record.recommendation_id), mapping=record.model_dump(mode="json"))
            await self.client.expire(self._key(record.recommendation_id), 604800)
        except (RedisError, OSError) as error:
            raise RecommendationUnavailable("Recommendation review store is unavailable.") from error
        return record

    async def get(self, recommendation_id: str) -> RecommendationRecord | None:
        try:
            payload = await self.client.hgetall(self._key(recommendation_id))
        except (RedisError, OSError) as error:
            raise RecommendationUnavailable("Recommendation review store is unavailable.") from error
        return RecommendationRecord.model_validate(payload) if payload else None

    async def decide(self, recommendation_id: str, decision: JobStatus, correction_notes: str = "") -> RecommendationRecord:
        if decision not in {JobStatus.APPROVED, JobStatus.REJECTED}:
            raise ValueError("Recommendation decisions must be approved or rejected.")
        record = await self.get(recommendation_id)
        if record is None:
            raise KeyError(recommendation_id)
        record.status = decision
        record.correction_notes = correction_notes
        try:
            await self.client.hset(self._key(recommendation_id), mapping={
                "status": decision.value,
                "correction_notes": correction_notes,
            })
        except (RedisError, OSError) as error:
            raise RecommendationUnavailable("Recommendation review store is unavailable.") from error
        return record

    async def close(self) -> None:
        await self.client.aclose()

    def _key(self, recommendation_id: str) -> str:
        return f"{self.key_prefix}{recommendation_id}"
