import fakeredis.aioredis
import pytest

from app import main


@pytest.fixture
def fake_redis(monkeypatch):
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(main.SEARCH_CACHE, "client", client)
    monkeypatch.setattr(main.JOB_QUEUE, "client", client)
    monkeypatch.setattr(main.RECOMMENDATION_STORE, "client", client)
    return client
