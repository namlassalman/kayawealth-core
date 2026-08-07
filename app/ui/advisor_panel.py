"""Advisor-only human-review controls for withheld recommendations."""

import httpx


def render_advisor_console(st, backend_url: str, append_message) -> None:
    """Render the persisted recommendation review gate for the advisor role."""
    if st.session_state.current_role != "Wealth Advisor":
        return

    report = st.session_state.active_agent_report
    if not report:
        return

    recommendation_id = report.get("recommendation_id")
    if not recommendation_id:
        st.info("No portfolio-change recommendation is awaiting advisor review.")
        return

    try:
        response = httpx.get(f"{backend_url}/api/v1/recommendations/{recommendation_id}", timeout=5.0)
        response.raise_for_status()
        record = response.json()
    except httpx.HTTPError as error:
        st.sidebar.error(f"Unable to load advisor review record: {error}")
        return

    status = record["status"]
    if status != "pending_review":
        st.info(f"Recommendation {recommendation_id} is already **{status}**.")
        return

    st.warning(f"⚠️ **System State: PENDING_REVIEW ({recommendation_id})** — client delivery is blocked.")
    st.markdown("### 📝 Advisor Review Panel")
    st.markdown(record["final_report"])
    notes = st.text_input(
        "Provide correction comments or refinement notes:",
        key=f"recommendation_notes_{recommendation_id}",
    )
    approve_column, reject_column = st.columns(2)

    if approve_column.button("✅ Approve Report to Client", key=f"approve_{recommendation_id}"):
        _submit_decision(st, backend_url, recommendation_id, "approved", notes)
        append_message("assistant", record["final_report"])
        st.success(f"Approved {recommendation_id} and dispatched it to the client history.")
        st.session_state.active_agent_report = None
        st.rerun()

    if reject_column.button("❌ Reject & Log Correction", key=f"reject_{recommendation_id}"):
        if not notes.strip():
            st.sidebar.warning("Please type correction notes before rejecting this recommendation.")
            return
        _submit_decision(st, backend_url, recommendation_id, "rejected", notes)
        append_message("assistant", "🔄 Advisor feedback logged. The recommendation was not delivered to the client.")
        st.session_state.active_agent_report = None
        st.rerun()


def _submit_decision(st, backend_url: str, recommendation_id: str, decision: str, notes: str) -> None:
    try:
        response = httpx.post(
            f"{backend_url}/api/v1/recommendations/{recommendation_id}/decision",
            json={"decision": decision, "correction_notes": notes.strip()},
            timeout=5.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as error:
        st.sidebar.error(f"Unable to save advisor decision: {error}")
        st.stop()
