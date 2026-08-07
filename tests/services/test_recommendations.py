import pytest

from app.models import JobStatus
from app.services.recommendations import RecommendationStore


@pytest.mark.asyncio
async def test_recommendation_requires_review_before_delivery(fake_redis):
    store = RecommendationStore("redis://unused")
    store.client = fake_redis
    record = await store.create("Rebalance my portfolio", "Proposed allocation change")
    assert record.status is JobStatus.PENDING_REVIEW

    approved = await store.decide(record.recommendation_id, JobStatus.APPROVED)
    assert approved.status is JobStatus.APPROVED
    await store.close()
