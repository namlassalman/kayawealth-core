"""Streamlit panel for the async mock market-tick demonstration."""

import asyncio
import json
from queue import Queue
from threading import Thread

import httpx


def render_market_tick_panel(st, backend_url: str) -> None:
    st.subheader("📈 Async Market Tick Stream")

    def request_stream() -> None:
        st.session_state.market_tick_should_stream = True

    st.caption("Choose a different ticker to stream five simulated ticks.")
    symbol = st.selectbox(
        "Demo symbol",
        ["AURA", "D05", "Z74", "C6L", "S58", "S63", "BN4", "U96", "9CI"],
        key="market_tick_symbol",
        on_change=request_stream,
    )
    if not st.session_state.pop("market_tick_should_stream", False):
        return

    placeholder = st.empty()
    received_ticks: list[dict] = []
    try:
        for tick in _stream_ticks(backend_url, symbol):
            received_ticks.append(tick)
            with placeholder.container():
                for item in received_ticks:
                    st.metric(
                        label=f"{item['sequence']}. {item['symbol']} · simulated",
                        value=f"${item['price']:.2f}",
                        delta=f"{item['change']:+.2f}",
                        delta_color="normal",
                    )
        st.success(f"Received {len(received_ticks)} simulated ticks from the async stream.")
    except RuntimeError as error:
        st.error(f"Market stream failed: {error}")


def _stream_ticks(backend_url: str, symbol: str):
    """Expose an async SSE stream as a synchronous generator for Streamlit rendering."""
    events: Queue[dict | Exception | None] = Queue()

    async def consume_stream() -> None:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                async with client.stream(
                    "GET",
                    f"{backend_url}/api/v1/market/ticks",
                    params={"symbol": symbol, "tick_count": 5, "interval_ms": 500},
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            events.put(json.loads(line.removeprefix("data: ")))
        except (httpx.HTTPError, json.JSONDecodeError) as error:
            events.put(error)
        finally:
            events.put(None)

    thread = Thread(target=lambda: asyncio.run(consume_stream()), daemon=True, name="aurawealth-market-stream")
    thread.start()
    while True:
        event = events.get()
        if event is None:
            return
        if isinstance(event, Exception):
            raise RuntimeError(str(event)) from event
        yield event
