"""Deterministic async market-data simulation for the streaming demonstration."""

import asyncio
from datetime import datetime, timezone


async def generate_market_ticks(symbol: str, tick_count: int, interval_seconds: float):
    """Yield simulated price ticks incrementally without external market-data calls."""
    normalized_symbol = symbol.upper()
    base_price = 100.0 + (sum(ord(character) for character in normalized_symbol) % 75)
    movements = (0.35, -0.18, 0.27, -0.11, 0.42, -0.24)

    for sequence in range(1, tick_count + 1):
        if sequence > 1 and interval_seconds:
            await asyncio.sleep(interval_seconds)
        movement = movements[(sequence - 1) % len(movements)]
        price = round(base_price + sum(movements[:sequence]), 2)
        yield {
            "symbol": normalized_symbol,
            "sequence": sequence,
            "price": price,
            "change": movement,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "simulated",
        }
