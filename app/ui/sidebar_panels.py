"""Optional Streamlit demonstration panels kept separate from the chat flow."""

import asyncio

import altair as alt
import httpx

from app.ui.market_panel import render_market_tick_panel


def render_sidebar_panels(st, backend_url: str, client_tools_expanded: bool = False) -> None:
    with st.sidebar.expander("👤 Client-facing tools", expanded=client_tools_expanded):
        _render_client_tools(st, backend_url, workspace_expanded=client_tools_expanded)
    with st.sidebar.expander("🧑‍💼 Wealth Advisor tools", expanded=False):
        _render_advisor_tools(st, backend_url)
    with st.sidebar.expander("⚙️ Operations Diagnostics", expanded=False):
        _render_operations_tools(st, backend_url)


def _render_client_tools(st, backend_url: str, workspace_expanded: bool = False) -> None:
    st.subheader("🔍 Metadata-Enhanced Hybrid Search")
    category_filter = st.selectbox(
        "Filter by Category:",
        [
            "", "tax_planning", "risk_management", "portfolio_rebalancing",
            "fixed_income", "estate_planning", "alternative_assets",
            "liquidity_management", "sustainable_investing",
            "regulatory_compliance", "macro_economics", "retirement_planning",
            "insurance_protection",
        ],
        key="hybrid_cat",
    )
    year_filter = st.selectbox("Filter by Recency Year:", [None, 2024, 2026], key="hybrid_year")
    search_query = st.text_input("Enter hybrid search query:", key="hybrid_query")
    if search_query:
        params = {"query": search_query, **({"category": category_filter} if category_filter else {}), **({"year": year_filter} if year_filter else {})}
        try:
            async def fetch_hybrid():
                async with httpx.AsyncClient() as client:
                    return await client.get(f"{backend_url}/api/v1/search/hybrid", params=params, timeout=10.0)
            response = asyncio.run(fetch_hybrid())
            response.raise_for_status()
            data = response.json()
            st.success(f"Found {data['total_results']} hybrid results!")
            active_filters = ", ".join(
                filter(
                    None,
                    [
                        f"category: {category_filter}" if category_filter else "",
                        f"year: {year_filter}" if year_filter else "",
                    ],
                )
            ) or "all categories and years"
            st.info(f"Showing the top matches for **“{search_query}”** using {active_filters}.")
            pools = data["source_breakdown"]
            st.caption(
                f"📊 Pools: Keyword [{pools['keyword_pool_size']}] | "
                f"Local embedding [{pools['semantic_pool_size']}]"
            )
            for index, match in enumerate(data["results"][:3]):
                # This panel already lives inside a sidebar expander. Streamlit
                # prohibits nesting a second expander, so result details remain
                # visible in compact containers instead.
                with st.container(border=True):
                    st.markdown(f"**Match {index + 1}: {match['id']}**")
                    st.write(f"Doc: {match['document_title']}")
                    st.write(f"Metadata: [Category: {match['category']} | Year: {match['recency_year']}]")
                    if "semantic_score" in match:
                        st.caption(f"Local embedding similarity: {match['semantic_score']:.4f}")
                    st.caption(f"Recency rerank score: {match['rerank_score']}")
                    st.caption(match["text"])
        except Exception as error:
            st.error(f"Could not connect to backend: {error}")

    st.markdown("---")
    st.subheader("🗺️ RAG Semantic Cluster Map")
    if st.checkbox("Show 1,200 document clusters", key="show_cluster_map"):
        try:
            response = httpx.get(f"{backend_url}/api/v1/rag/clusters", timeout=10.0)
            response.raise_for_status()
            cluster_data = response.json()
            st.caption(f"{cluster_data['total_points']} chunks grouped by thematic metadata")
            category_centers = {
                category: (sum(point["cluster_x"] for point in cluster_data["points"] if point["category"] == category), sum(point["cluster_y"] for point in cluster_data["points"] if point["category"] == category))
                for category in {point["category"] for point in cluster_data["points"]}
            }
            categories = sorted(category_centers, key=lambda category: (category_centers[category][0], -category_centers[category][1]))
            colors = ["#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F", "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC", "#2F4B7C", "#A05195"]
            chart = alt.Chart(alt.Data(values=cluster_data["points"])).mark_circle(
                size=48 if workspace_expanded else 24,
                opacity=0.65,
            ).encode(
                x=alt.X("cluster_x:Q", title="Cluster X", axis=alt.Axis(labelFontSize=9)),
                y=alt.Y("cluster_y:Q", title="Cluster Y", axis=alt.Axis(labelFontSize=9)),
                color=alt.Color("category:N", legend=None, scale=alt.Scale(domain=categories, range=colors)), tooltip=["id:N", "category:N"],
            ).properties(
                width="container" if workspace_expanded else 250,
                height=500 if workspace_expanded else 250,
            )
            st.altair_chart(chart, use_container_width=workspace_expanded)
            if workspace_expanded:
                legend_columns = st.columns(4)
                for index, (category, color) in enumerate(zip(categories, colors)):
                    with legend_columns[index // 3]:
                        st.markdown(
                            f"<span style='color:{color}; font-size:1.35rem; vertical-align:middle'>●</span> "
                            f"<span style='vertical-align:middle'>{category}</span>",
                            unsafe_allow_html=True,
                        )
            else:
                for category, color in zip(categories, colors):
                    st.markdown(f"<span style='color:{color}; font-size:1.6rem; vertical-align:middle'>●</span> <span style='vertical-align:middle'>{category}</span>", unsafe_allow_html=True)
        except Exception as error:
            st.error(f"Cluster map failed: {error}")


def _render_advisor_tools(st, backend_url: str) -> None:
    st.subheader("⚖️ Golden-Set Groundedness Eval")
    golden_cases = {
        "retirement_risk": "Review my retirement portfolio risk.", "tax_planning": "Help me plan for tax-efficient investing.",
        "rebalancing": "Should I rebalance my portfolio?", "liquidity": "Assess liquidity for my upcoming expense.",
        "estate": "What should I consider for estate planning?",
    }
    selected_case = st.selectbox("Golden test case", list(golden_cases), format_func=lambda case_id: golden_cases[case_id])
    if st.button("Evaluate latest assistant response"):
        latest_response = next((message["content"] for message in reversed(st.session_state.messages) if message["role"] == "assistant"), "")
        try:
            response = httpx.post(f"{backend_url}/api/v1/evaluations/groundedness", json={"case_id": selected_case, "response": latest_response}, timeout=10.0)
            response.raise_for_status()
            evaluation = response.json()
            st.metric("Groundedness", f"{evaluation['groundedness_score']}%")
            st.caption(f"{evaluation['verdict']} — Missing: {', '.join(evaluation['missing_signals']) or 'None'}")
        except Exception as error:
            st.error(f"Evaluation failed: {error}")

    st.markdown("---")
    st.subheader("👑 Hierarchical Agent Demo")
    query = st.text_input("Manager request", value="Review my retirement portfolio risk.", key="hierarchical_query")
    if st.button("Run manager-led workflow"):
        try:
            response = httpx.post(f"{backend_url}/api/v1/agents/hierarchical", json={"user_query": query, "session_token": st.session_state.session_token}, timeout=10.0)
            response.raise_for_status()
            result = response.json()
            st.caption(f"Manager route: {result['manager_route']}")
            st.caption(f"Delegated to: {', '.join(result['delegated_agents'])}")
            st.caption(f"Dialogue focus: {result['dialogue_state']['focus']}")
            st.markdown(result["final_report"])
        except Exception as error:
            st.error(f"Hierarchical workflow failed: {error}")


def _render_operations_tools(st, backend_url: str) -> None:
    st.subheader("🌍 Environment Profile")
    if st.button("Inspect active configuration"):
        try:
            response = httpx.get(f"{backend_url}/api/v1/system/config", timeout=10.0)
            response.raise_for_status()
            config = response.json()
            st.success(f"Active profile: {config['environment']}")
            st.caption(
                f"Cache TTL: {config['cache_ttl_seconds']}s | "
                f"Queue retention: {config['queue_job_ttl_seconds']}s"
            )
        except Exception as error:
            st.error(f"Configuration check failed: {error}")

    st.markdown("---")
    render_market_tick_panel(st, backend_url)

    st.markdown("---")
    st.subheader("⚡ Redis Cache Validation")
    cache_query = st.text_input("Search query to cache", key="cache_query")
    if st.button("Run cached search"):
        try:
            response = httpx.get(f"{backend_url}/api/v1/search/cached", params={"query": cache_query}, timeout=10.0)
            response.raise_for_status()
            cache_data = response.json()
            st.success(f"{'HIT' if cache_data['cache_hit'] else 'MISS'} via {cache_data['cache_backend']}")
            st.caption(f"TTL: {cache_data['ttl_seconds']} seconds")
        except Exception as error:
            st.error(f"Cache check failed: {error}")

    st.markdown("---")
    st.subheader("📬 Redis FIFO Queue Validation")
    st.session_state.setdefault("demo_queue_jobs", [])
    if st.button("Queue 3 ordered demo jobs"):
        try:
            response = httpx.post(f"{backend_url}/api/v1/queue/demo-batch", timeout=10.0)
            response.raise_for_status()
            st.session_state.demo_queue_jobs = response.json()["jobs"]
            st.success("Queued jobs 1 → 2 → 3 for one worker.")
        except Exception as error:
            st.error(f"Queue submission failed: {error}")
    if st.session_state.demo_queue_jobs and st.button("Check queued job status"):
        try:
            for job in st.session_state.demo_queue_jobs:
                response = httpx.get(f"{backend_url}/api/v1/queue/job/{job['job_id']}", timeout=10.0)
                response.raise_for_status()
                status = response.json()
                st.caption(f"#{status['submitted_order']} — {status['status']} ({status['progress']}%)")
        except Exception as error:
            st.error(f"Queue status failed: {error}")
