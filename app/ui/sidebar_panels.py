"""Optional Streamlit demonstration panels kept separate from the chat flow."""

import asyncio

import altair as alt
import httpx


def render_sidebar_panels(st, backend_url: str) -> None:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Metadata-Enhanced Hybrid Search")
    category_filter = st.sidebar.selectbox("Filter by Category:", ["", "tax_planning", "risk_management", "portfolio_rebalancing", "macro_economics"], key="hybrid_cat")
    year_filter = st.sidebar.selectbox("Filter by Recency Year:", [None, 2024, 2026], key="hybrid_year")
    search_query = st.sidebar.text_input("Enter hybrid search query:", key="hybrid_query")
    if search_query:
        params = {"query": search_query, **({"category": category_filter} if category_filter else {}), **({"year": year_filter} if year_filter else {})}
        try:
            async def fetch_hybrid():
                async with httpx.AsyncClient() as client:
                    return await client.get(f"{backend_url}/api/v1/search/hybrid", params=params, timeout=10.0)
            response = asyncio.run(fetch_hybrid())
            response.raise_for_status()
            data = response.json()
            st.sidebar.success(f"Found {data['total_results']} hybrid results!")
            pools = data["source_breakdown"]
            st.sidebar.caption(f"📊 Pools: Keyword [{pools['keyword_pool_size']}] | Vector [{pools['semantic_pool_size']}]")
            for index, match in enumerate(data["results"][:3]):
                with st.sidebar.expander(f"Match {index + 1}: {match['id']}"):
                    st.write(f"Doc: {match['document_title']}")
                    st.write(f"Metadata: [Category: {match['category']} | Year: {match['recency_year']}]")
                    st.caption(match["text"])
        except Exception as error:
            st.sidebar.error(f"Could not connect to backend: {error}")

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚖️ Golden-Set Groundedness Eval")
    golden_cases = {
        "retirement_risk": "Review my retirement portfolio risk.", "tax_planning": "Help me plan for tax-efficient investing.",
        "rebalancing": "Should I rebalance my portfolio?", "liquidity": "Assess liquidity for my upcoming expense.",
        "estate": "What should I consider for estate planning?",
    }
    selected_case = st.sidebar.selectbox("Golden test case", list(golden_cases), format_func=lambda case_id: golden_cases[case_id])
    if st.sidebar.button("Evaluate latest assistant response"):
        latest_response = next((message["content"] for message in reversed(st.session_state.messages) if message["role"] == "assistant"), "")
        try:
            response = httpx.post(f"{backend_url}/api/v1/evaluations/groundedness", json={"case_id": selected_case, "response": latest_response}, timeout=10.0)
            response.raise_for_status()
            evaluation = response.json()
            st.sidebar.metric("Groundedness", f"{evaluation['groundedness_score']}%")
            st.sidebar.caption(f"{evaluation['verdict']} — Missing: {', '.join(evaluation['missing_signals']) or 'None'}")
        except Exception as error:
            st.sidebar.error(f"Evaluation failed: {error}")

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ Redis Cache Validation")
    cache_query = st.sidebar.text_input("Search query to cache", key="cache_query")
    if st.sidebar.button("Run cached search"):
        try:
            response = httpx.get(f"{backend_url}/api/v1/search/cached", params={"query": cache_query}, timeout=10.0)
            response.raise_for_status()
            cache_data = response.json()
            st.sidebar.success(f"{'HIT' if cache_data['cache_hit'] else 'MISS'} via {cache_data['cache_backend']}")
            st.sidebar.caption(f"TTL: {cache_data['ttl_seconds']} seconds")
        except Exception as error:
            st.sidebar.error(f"Cache check failed: {error}")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🗺️ RAG Semantic Cluster Map")
    if st.sidebar.checkbox("Show 1,000 document clusters", key="show_cluster_map"):
        try:
            response = httpx.get(f"{backend_url}/api/v1/rag/clusters", timeout=10.0)
            response.raise_for_status()
            cluster_data = response.json()
            st.sidebar.caption(f"{cluster_data['total_points']} chunks grouped by thematic metadata")
            category_centers = {
                category: (sum(point["cluster_x"] for point in cluster_data["points"] if point["category"] == category), sum(point["cluster_y"] for point in cluster_data["points"] if point["category"] == category))
                for category in {point["category"] for point in cluster_data["points"]}
            }
            categories = sorted(category_centers, key=lambda category: (category_centers[category][0], -category_centers[category][1]))
            colors = ["#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F", "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC"]
            chart = alt.Chart(alt.Data(values=cluster_data["points"])).mark_circle(size=24, opacity=0.65).encode(
                x=alt.X("cluster_x:Q", title="Cluster X", axis=alt.Axis(labelFontSize=9)),
                y=alt.Y("cluster_y:Q", title="Cluster Y", axis=alt.Axis(labelFontSize=9)),
                color=alt.Color("category:N", legend=None, scale=alt.Scale(domain=categories, range=colors)), tooltip=["id:N", "category:N"],
            ).properties(width=250, height=250)
            st.sidebar.altair_chart(chart, use_container_width=False)
            for category, color in zip(categories, colors):
                st.sidebar.markdown(f"<span style='color:{color}; font-size:1.6rem; vertical-align:middle'>●</span> <span style='vertical-align:middle'>{category}</span>", unsafe_allow_html=True)
        except Exception as error:
            st.sidebar.error(f"Cluster map failed: {error}")

    st.sidebar.markdown("---")
    st.sidebar.subheader("📬 Redis FIFO Queue Validation")
    st.session_state.setdefault("demo_queue_jobs", [])
    if st.sidebar.button("Queue 3 ordered demo jobs"):
        try:
            response = httpx.post(f"{backend_url}/api/v1/queue/demo-batch", timeout=10.0)
            response.raise_for_status()
            st.session_state.demo_queue_jobs = response.json()["jobs"]
            st.sidebar.success("Queued jobs 1 → 2 → 3 for one worker.")
        except Exception as error:
            st.sidebar.error(f"Queue submission failed: {error}")
    if st.session_state.demo_queue_jobs and st.sidebar.button("Check queued job status"):
        try:
            for job in st.session_state.demo_queue_jobs:
                response = httpx.get(f"{backend_url}/api/v1/queue/job/{job['job_id']}", timeout=10.0)
                response.raise_for_status()
                status = response.json()
                st.sidebar.caption(f"#{status['submitted_order']} — {status['status']} ({status['progress']}%)")
        except Exception as error:
            st.sidebar.error(f"Queue status failed: {error}")

    st.sidebar.markdown("---")
    st.sidebar.subheader("👑 Hierarchical Agent Demo")
    query = st.sidebar.text_input("Manager request", value="Review my retirement portfolio risk.", key="hierarchical_query")
    if st.sidebar.button("Run manager-led workflow"):
        try:
            response = httpx.post(f"{backend_url}/api/v1/agents/hierarchical", json={"user_query": query, "session_token": st.session_state.session_token}, timeout=10.0)
            response.raise_for_status()
            result = response.json()
            st.sidebar.caption(f"Manager route: {result['manager_route']}")
            st.sidebar.caption(f"Delegated to: {', '.join(result['delegated_agents'])}")
            st.sidebar.caption(f"Dialogue focus: {result['dialogue_state']['focus']}")
            st.sidebar.markdown(result["final_report"])
        except Exception as error:
            st.sidebar.error(f"Hierarchical workflow failed: {error}")
