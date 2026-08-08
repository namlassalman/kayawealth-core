import httpx
import pytest
import json

from app.services.http_client import post_json


@pytest.mark.asyncio
async def test_post_json_uses_async_transport_and_preserves_response():
    received: dict = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        received["method"] = request.method
        received["path"] = request.url.path
        received["payload"] = json.loads(request.content)
        return httpx.Response(200, json={"final_report": "Safe response"})

    response = await post_json(
        "http://test/api/v1/orchestrator/route",
        {"user_query": "Hello", "session_token": "session"},
        transport=httpx.MockTransport(handler),
    )

    assert response.json()["final_report"] == "Safe response"
    assert received == {
        "method": "POST",
        "path": "/api/v1/orchestrator/route",
        "payload": {"user_query": "Hello", "session_token": "session"},
    }
