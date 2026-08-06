import streamlit as st
import httpx
import asyncio

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AuraWealth Command Center", page_icon="💼", layout="centered")

st.title("💼 AuraWealth Client Portal")
st.caption("Enterprise Async Core Running Natively on Python 3.11")

# Initialize state-persistent memory array
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to AuraWealth. Type 'simulate' or ask a wealth planning question to begin."}
    ]

# Render historic message threads natively across top-to-bottom re-runs
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Capture live user conversational inputs
if user_input := st.chat_input("Ask AuraWealth..."):
    # Append user intent to session matrix memory
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Scenario A: User triggers the Portfolio Simulation Workflow
    if "simulate" in user_input.lower():
        bot_notice = "System triggered portfolio matrix simulation. Handing off payload to FastAPI queue..."
        st.chat_message("assistant").write(bot_notice)
        st.session_state.messages.append({"role": "assistant", "content": bot_notice})
        
        mock_payload = {
            "portfolio_name": "AuraWealth Growth Alpha",
            "initial_capital": 50000.0,
            "horizon_years": 12
        }
        
        async def trigger_and_poll():
            async with httpx.AsyncClient() as client:
                # 1. Dispatch post to background tasks router
                res = await client.post(f"{BACKEND_URL}/api/v1/simulate", json=mock_payload, timeout=10.0)
                if res.status_code != 202:
                    return "Error contacting core engine infrastructure."
                
                task_id = res.json()["task_id"]
                
                # 2. Continuous non-blocking poll matrix until execution wraps up
                with st.spinner("Processing deep portfolio calculations asynchronously..."):
                    for _ in range(20):
                        await asyncio.sleep(0.5)
                        status_res = await client.get(f"{BACKEND_URL}/api/v1/tasks/{task_id}")
                        task_data = status_res.json()
                        
                        if task_data["status"] == "completed":
                            return f"🎉 **Simulation Complete!** Portfolio: `{task_data['portfolio_name']}` | Projected Yield: **${task_data['expected_return']:,}** (Processed asynchronously via background worker threads)."
                return "Calculation task timed out on queue."

        result_text = asyncio.run(trigger_and_poll())
        st.chat_message("assistant").write(result_text)
        st.session_state.messages.append({"role": "assistant", "content": result_text})
        
    # Scenario B: Standard multi-turn placeholder fallback
    else:
        reply_text = f"AuraWealth Core caught request: '{user_input}'. Routing framework configuration is live."
        st.chat_message("assistant").write(reply_text)
        st.session_state.messages.append({"role": "assistant", "content": reply_text})

# --- UPGRADED TESTING SANDBOX FOR ISSUES #3 & #22 ---
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Metadata-Enhanced Search")

# Interactive dropdown selectors for metadata attributes
category_filter = st.sidebar.selectbox(
    "Filter by Category:", 
    ["", "tax_planning", "risk_management", "portfolio_rebalancing", "macro_economics"]
)
year_filter = st.sidebar.selectbox("Filter by Recency Year:", [None, 2024, 2026])

search_query = st.sidebar.text_input("Enter search keyword:")

if search_query:
    try:
        with st.sidebar.spinner("Querying knowledge base..."):
            # Build payload with metadata parameters
            params = {"query": search_query}
            if category_filter:
                params["category"] = category_filter
            if year_filter:
                params["year"] = year_filter
                
            response = httpx.get(f"{BACKEND_URL}/api/v1/search/keyword", params=params)
            
            if response.status_code == 200:
                data = response.json()
                st.sidebar.success(f"Found {data['total_matches_found']} filtered matches!")
                
                if data["results"]:
                    top_match = data["results"][0]
                    with st.sidebar.expander(f"Top Match: {top_match['id']}"):
                        st.write(f"**Doc:** {top_match['document_title']}")
                        st.write(f"**Metadata Tags:** [Category: `{top_match['category']}` | Year: `{top_match['recency_year']}`]")
                        st.caption(top_match["text"])
            else:
                st.sidebar.error("Backend search failed.")
    except Exception as e:
        st.sidebar.error("Could not connect to backend.")

