import pytest

from app.services.market_data import generate_market_ticks


@pytest.mark.asyncio
async def test_async_market_tick_generator_emits_ordered_simulated_ticks():
    ticks = [
        tick async for tick in generate_market_ticks("AURA", tick_count=3, interval_seconds=0)
    ]

    assert [tick["sequence"] for tick in ticks] == [1, 2, 3]
    assert all(tick["symbol"] == "AURA" for tick in ticks)
    assert all(isinstance(tick["price"], float) for tick in ticks)
    assert ticks[0]["price"] != ticks[1]["price"]
