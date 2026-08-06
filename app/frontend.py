import streamlit as st
import httpx
import asyncio

# Configure the local FastAPI backend endpoint
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="KayaWealth Core", page_icon="💼", layout="centered")

st.title("💼 KayaWealth Core Dashboard")
st.caption("Pyenv Python 3.11 Engine running on Pop!_OS")

st.subheader("Portfolio Simulation Launcher")

# Form inputs matching the backend Pydantic model
with st.form("simulation_form"):
    portfolio_name = st.text_input("Portfolio Name", value="Growth Alpha")
    initial_capital = st.number_input("Initial Capital ($)", min_value=0.0, value=10000.0, step=1000.0)
    horizon_years = st.slider("Investment Horizon (Years)", min_value=1, max_value=30, value=10)
    submit_button = st.form_submit_button(label="Run Async Simulation")

async def fetch_simulation(payload):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BACKEND_URL}/api/v1/simulate", json=payload, timeout=10.0)
        return response

if submit_button:
    payload = {
        "portfolio_name": portfolio_name,
        "initial_capital": initial_capital,
        "horizon_years": horizon_years
    }
    
    st.info("Sending asynchronous request to FastAPI backend...")
    
    try:
        # Resolve the async HTTP request within Streamlit's synchronous execution
        response = asyncio.run(fetch_simulation(payload))
        
        if response.status_code == 200:
            data = response.json()
            st.success("Simulation complete!")
            
            # Display metrics visually
            col1, col2 = st.columns(2)
            col1.metric("Portfolio", data["portfolio_name"])
            col2.metric("Projected Return", f"${data['expected_return']:,}")
            
            st.json(data)
        else:
            st.error(f"Backend returned an error: {response.status_code}")
    except httpx.ConnectError:
        st.error(f"Could not connect to backend at {BACKEND_URL}. Is your FastAPI server running?")
