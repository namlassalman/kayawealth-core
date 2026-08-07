import streamlit as st
import httpx
import requests
import json, os, time, uuid
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ui.sidebar_panels import render_sidebar_panels

BACKEND_URL = "http://127.0.0.1:8000"
SESSION_FILE = os.getenv("AURAWEALTH_SESSION_FILE", "history_session.json")

st.set_page_config(page_title="AuraWealth Command Center", page_icon="💼", layout="centered")

st.title("💼 AuraWealth Client Portal")
st.caption("Enterprise Async Core Running Natively on Python 3.11")

# --- CENTRAL ROLE MANAGEMENT ENGINE ---
if "current_role" not in st.session_state:
    st.session_state.current_role = "Client"  # Defaults safely to Client persona

# --- CENTRAL ROLE MANAGEMENT ENGINE (Fixed Toggle) ---
if "current_role" not in st.session_state:
    st.session_state.current_role = "Client"

# Direct callback function to update state instantly on a single click
def on_role_change():
    st.session_state.current_role = st.session_state.role_radio_widget

st.sidebar.title("🎭 Identity Access Management")
st.sidebar.radio(
    "Select Active Portal View:",
    ["Client", "Wealth Advisor"],
    key="role_radio_widget",
    index=0 if st.session_state.current_role == "Client" else 1,
    on_change=on_role_change
)

st.sidebar.markdown(f"Active Session Context: **`{st.session_state.current_role} Mode`**")

# --- INITIALIZE STATE-PERSISTENT SESSION MEMORY (Issue 10) ---
if "session_token" not in st.session_state:
    st.session_state.session_token = str(uuid.uuid4())

# 1. Attempt to restore state from disk storage file first
if "messages" not in st.session_state:
    st.session_state.messages = []
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                st.session_state.messages = json.load(f)
        except:
            st.session_state.messages = []
            
    # Fallback to standard welcome message if disk file is missing or corrupt
    if not st.session_state.messages:
        st.session_state.messages = [
            {"role": "assistant", "content": "Welcome to AuraWealth. Use the Quick Actions below or ask a wealth planning question to begin."}
        ]

def persist_messages() -> None:
    """Synchronize the active chat history before Streamlit reruns."""
    with open(SESSION_FILE, "w") as f:
        json.dump(st.session_state.messages, f, indent=4)

def append_message(role: str, content: str) -> None:
    st.session_state.messages.append({"role": role, "content": content})
    persist_messages()

def record_response_feedback(rating: str, critique: str = "") -> None:
    """Persist a rating with the exact client prompt and assistant response it evaluates."""
    logs = []
    if os.path.exists("feedback_logs.json"):
        try:
            with open("feedback_logs.json", "r") as f:
                logs = json.load(f)
        except (json.JSONDecodeError, OSError):
            logs = []

    last_user_prompt = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"), "Conversational Query")
    last_response = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "assistant"), "")
    logs.append({
        "event_type": "response_rating",
        "rating": rating,
        "user_query": last_user_prompt,
        "assistant_response": last_response,
        "advisor_critique": critique,
        "session_token": st.session_state.session_token,
        "timestamp": time.time(),
    })
    with open("feedback_logs.json", "w") as f:
        json.dump(logs, f, indent=4)

def render_operational_trace(events: list[dict]) -> None:
    for event in events:
        st.caption(f"{event['timestamp']} · {event['node']} · {event['outcome']}")
        st.write(event['details'])

if "active_agent_report" not in st.session_state:
    st.session_state.active_agent_report = None

if "queue_index" not in st.session_state:
    st.session_state.queue_index = 0

if "active_trigger" not in st.session_state:
    st.session_state.active_trigger = None

if "dialogue_state" not in st.session_state:
    st.session_state.dialogue_state = None


# --- DYNAMIC INTERACTIVE QUICK ACTIONS ---
st.markdown(f"### 🚀 Quick Actions ({st.session_state.current_role} Tier)")

if st.session_state.current_role == "Client":
    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("📱 Ask Platform Purpose"):
        st.session_state.active_trigger = "purpose"
        st.rerun()
    if col_btn2.button("📈 Request Portfolio Rebalance"):
        st.session_state.active_trigger = "rebalance"
        st.rerun()
else:
    if st.button("👑 Initialize Pending Audit Review Queue"):
        st.session_state.active_trigger = "simulation"
        st.rerun()

st.markdown("---")

if st.session_state.dialogue_state:
    st.sidebar.caption(f"Dialogue focus: {st.session_state.dialogue_state['focus']}")
    if st.session_state.dialogue_state.get("transition"):
        st.sidebar.caption(f"Context switch: {st.session_state.dialogue_state['transition']}")

# Render historic message threads natively across top-to-bottom re-runs
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if st.session_state.active_agent_report and st.session_state.active_agent_report.get("operational_trace"):
    with st.expander("🔍 Show Multi-Agent Operational Trace Logs"):
        render_operational_trace(st.session_state.active_agent_report["operational_trace"])

# Capture live user conversational inputs
user_input = st.chat_input("Ask AuraWealth...")

current_query = None
if st.session_state.active_trigger:
    if st.session_state.active_trigger == "purpose":
        current_query = "What is this application used for?"
    elif st.session_state.active_trigger == "rebalance":
        current_query = "I want to run an asset simulation and rebalance my high-risk tax portfolio"
    elif st.session_state.active_trigger == "simulation":
        current_query = "run agent simulation"
    st.session_state.active_trigger = None
elif user_input:
    current_query = user_input

# --- PROCESS ACTIVE INCOMING INQUIRIES ---
if current_query:
    st.chat_message("user").write(current_query)
    append_message("user", current_query)
    
    complex_triggers = ["simulate", "agent", "portfolio", "rebalance", "optimization"]
    is_complex = any(word in current_query.lower() for word in complex_triggers)
    
    with st.spinner("AuraWealth processing query..."):
        try:
            res = httpx.post(
                f"{BACKEND_URL}/api/v1/orchestrator/route",
                json={"user_query": current_query, "session_token": st.session_state.session_token},
                timeout=10.0
            )
            if res.status_code == 400:
                reply_text = f"🛡️ {res.json().get('detail', 'Security policy blocked this request.')}"
                report_payload = {"final_report": reply_text, "guardrail_blocked": True}
            else:
                res.raise_for_status()
                report_payload = res.json()
                reply_text = report_payload.get("final_report", "Error generating response.")
                st.sidebar.caption(f"Workflow route: {report_payload.get('route', 'security_block')}")
                if report_payload.get("dialogue_state"):
                    st.session_state.dialogue_state = report_payload["dialogue_state"]
            
            append_message("assistant", reply_text)
            st.session_state.active_agent_report = report_payload
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Core Engine connection failed: {str(e)}")

# --- CONSOLIDATED FEEDBACK GENERATOR INJECTED IN WORKSPACE ---
if len(st.session_state.messages) > 1 and st.session_state.messages[-1]["role"] == "assistant":
    if "show_critique_box" not in st.session_state:
        st.session_state.show_critique_box = False

    st.markdown("---")
    st.caption("🛡️ **System Performance Telemetry Verification**")
    c1, c2, _ = st.columns(3)
    
    if c1.button("👍", key="global_thumb_up"):
        record_response_feedback("up")
        st.sidebar.success("Feedback saved!")
        st.session_state.show_critique_box = False
        
    if c2.button("👎", key="global_thumb_down"):
        st.session_state.show_critique_box = True

    if st.session_state.show_critique_box:
        with st.form("response_critique_form"):
            critique_input = st.text_input("What went wrong with this response?")
            submitted = st.form_submit_button("Save feedback")
        if submitted and critique_input.strip():
            record_response_feedback("down", critique_input.strip())
            st.sidebar.warning("Critique saved to disk!")
            st.session_state.show_critique_box = False
            st.rerun()


# --- PERSISTENT ADVISOR CONSOLE LAYER ---
if st.session_state.current_role == "Wealth Advisor" and st.session_state.active_agent_report:
    try:
        queue_res = httpx.get(f"{BACKEND_URL}/api/v1/queue/next", params={"current_index": st.session_state.queue_index})
        queue_data = queue_res.json()
        
        if queue_data["status"] == "empty":
            st.success("🎉 **Queue Cleared!** All pending audit reviews are complete.")
            st.session_state.active_agent_report = None
            st.session_state.queue_index = 0
        else:
            item = queue_data["item"]
            st.warning(f"⚠️ **System State: PENDING_REVIEW ({item['ticket_id']})** — Verification mandatory.")
            
            with st.expander("🔍 Show Multi-Agent Operational Trace Logs"):
                trace_events = st.session_state.active_agent_report.get("operational_trace", [])
                if trace_events:
                    render_operational_trace(trace_events)
                else:
                    st.text(item["intake_data"])
                    st.text(item["risk_assessment"])
            
            st.markdown("### 📝 Advisor Review Panel")
            st.markdown(item["final_report"])
            
            critique_notes = st.text_input("Provide correction comments or refinement notes:", key=f"critique_{item['ticket_id']}")
            col1, col2 = st.columns(2)
            
            if col1.button("✅ Approve Report to Client"):
                st.success(f"Dispatched {item['ticket_id']} straight to client profile.")
                append_message("assistant", item["final_report"])
                st.session_state.queue_index += 1
                st.rerun()
                
            if col2.button("❌ Reject & Log Correction"):
                if critique_notes:
                    requests.post(
                        f"{BACKEND_URL}/api/v1/feedback/log",
                        json={"query": item["user_query"], "critique": critique_notes},
                        timeout=5.0
                    )
                    st.sidebar.success(f"Critique for {item['ticket_id']} successfully synchronized to disk!")
                    append_message("assistant", f"🔄 Advisor Feedback Logged for {item['ticket_id']}: {critique_notes}")
                    st.session_state.queue_index += 1
                    st.rerun()
                else:
                    st.sidebar.warning("Please type your critique notes before clicking Reject.")
                    
    except Exception as e:
        st.sidebar.error(f"Failed to fetch next queue packet: {str(e)}")

render_sidebar_panels(st, BACKEND_URL)
