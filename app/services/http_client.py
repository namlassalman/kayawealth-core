"""Async HTTP transport helpers for Streamlit-triggered backend calls."""

import asyncio
from collections.abc import Awaitable
from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar

import httpx


Result = TypeVar("Result")


async def post_json(
    url: str,
    payload: dict,
    *,
    timeout_seconds: float = 10.0,
    transport: httpx.AsyncBaseTransport | None = None,
) -> httpx.Response:
    """Send JSON through a short-lived `httpx.AsyncClient`."""
    async with httpx.AsyncClient(timeout=timeout_seconds, transport=transport) as client:
        return await client.post(url, json=payload)


def run_async(coroutine: Awaitable[Result]) -> Result:
    """Bridge Streamlit's synchronous script execution to an async request.

    Streamlit normally runs application scripts without an active event loop.
    If an embedding runtime provides one, execute the coroutine in a short-lived
    worker thread instead of nesting event loops in the current thread.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coroutine)
    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="aurawealth-http") as executor:
        return executor.submit(asyncio.run, coroutine).result()
