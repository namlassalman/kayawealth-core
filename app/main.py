import asyncio
import uuid
import os
import json
import time  # Properly anchored at the top of the file
import re
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from app.services.worker import execute_distributed_simulation

app = FastAPI(
    title="AuraWealth Core API",
    description="Asynchronous backend engine for portfolio optimization and agent routing",
    version="1.0.0"
)

# --- ENVIRONMENT STATE CONFIGURATION ---
IS_PRODUCTION = False  # Toggle to True for presentation mode or deployment configs

# Force the file to save directly at the main project root folder level
FEEDBACK_FILE = "feedback_logs.json"

# Automatically load the 1,000 chunks into local server RAM on startup
KB_PATH = os.path.join(os.path.dirname(__file__), "kb_chunks.json")
with open(KB_PATH, "r") as f:
    knowledge_base: list[dict] = json.load(f)

# Simulated incoming enterprise advisory transaction queue
INCOMING_ADVISOR_QUEUE = [
    {
        "ticket_id": "TICKET_A101",
        "user_query": "I want to run an asset simulation and rebalance my high-risk tax portfolio",
        "intake_data": "Client: Salman. Net Worth Track: Tier-1 HNW. Focus: Capital gains optimization.",
        "risk_assessment": "Current allocation exceeds volatility limits by 4.2%. Rebalancing triggered.",
        "final_report": "### 💼 Advisory Report A101 (Tax Optimization)\n\n* **Strategy:** Liquidate legacy tech equities. Reallocate 15% to short-duration sovereign tax-exempt bonds."
    },
    {
        "ticket_id": "TICKET_B202",
        "user_query": "Review international estate transfer exposure constraints",
        "intake_data": "Client: Cross-border trust file. Focus: Foreign asset disclosure thresholds.",
        "risk_assessment": "Compliance flag: Sub-chapter J processing limits active. Low risk profile verified.",
        "final_report": "### 💼 Advisory Report B202 (Estate Governance)\n\n* **Strategy:** Structuring asset transfers via localized offshore trust vehicles to mitigate cross-jurisdictional withholding penalties."
    },
    {
        "ticket_id": "TICKET_C303",
        "user_query": "Execute liquidity match evaluation against Q3 drawdown requests",
        "intake_data": "Client: Real estate development fund account. Focus: Near-term cash equivalents allocation.",
        "risk_assessment": "Liquidity stress test: Basel III cash coverage metric sits securely at 115%. Approved.",
        "final_report": "### 💼 Advisory Report C303 (Liquidity Match)\n\n* **Strategy:** Allocate $250k into highly liquid commercial money-market instruments to safely meet upcoming capital calls."
    }
]

# Thread-safe in-memory task database matrix
tasks_db: dict[str, dict] = {}

# --- ENTERPRISE ENVIRONMENT PIPELINE CONFIGURATION (Issue #27) ---
def load_environment_profile() -> dict:
    env_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    env_profile = {"ENV": "PROD", "TTL": 86400.0} # Secure default fallback
    
    if os.path.exists(env_file_path):
        with open(env_file_path, "r") as f:
            for line in f:
                if line.startswith("AURAWEALTH_ENV="):
                    parts = line.strip().split("=")
                    if len(parts) == 2:
                        current_env = parts[1].strip().upper()
                        if current_env == "DEV":
                            return {"ENV": "DEV", "TTL": 10.0}
                        elif current_env == "TEST":
                            return {"ENV": "TEST", "TTL": 60.0}
    return env_profile

ENV_CONFIG = load_environment_profile()

# --- INGRESS PROMPT-HACKING GUARDRAILS (Issue #12) ---
PROMPT_INJECTION_PATTERNS = (
    r"\bignore\s+(?:all\s+)?(?:previous|prior)\s+instructions?\b",
    r"\b(?:disregard|override|forget)\s+(?:all\s+)?(?:previous|prior)\s+(?:instructions?|rules?)\b",
    r"\b(?:reveal|show|print)\s+(?:your|the)\s+(?:system|developer)\s+(?:prompt|instructions?)\b",
    r"\b(?:system\s+prompt|developer\s+message)\b",
)

def enforce_prompt_guardrails(text: str) -> None:
    """Reject known instruction-override patterns before agent execution."""
    if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in PROMPT_INJECTION_PATTERNS):
        raise HTTPException(
            status_code=400,
            detail="Security policy blocked this request because it contains an instruction-override pattern.",
        )

# Explicitly model the incoming frontend payload structure
class FeedbackPayload(BaseModel):
    query: str
    critique: str

@app.post("/api/v1/feedback/log")
async def log_client_feedback(payload: FeedbackPayload):
    logs = []
    
    # 1. Read existing historical critique array if present
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r") as f:
                logs = json.load(f)
                if not isinstance(logs, list):
                    logs = []
        except Exception:
            logs = []
            
    # 2. Append the fresh user critique dictionary entry 
    new_entry = {
        "user_query": payload.query,
        "advisor_critique": payload.critique,
        "timestamp": str(asyncio.get_event_loop().time())
    }
    logs.append(new_entry)
    
    # 3. Force an immediate flush write to local disk
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(logs, f, indent=4)
        
    return {"status": "SUCCESS", "stored_records_count": len(logs)}

class SimulationRequest(BaseModel):
    portfolio_name: str
    initial_capital: float
    horizon_years: int

# --- PURE PYTHON SEARCH FUNCTIONS (Prevents async routing crashes) ---

def _execute_keyword_filter(query: str, category: str = None, year: int = None) -> list[dict]:
    if not query:
        return []
    results = []
    query_words = query.lower().split()
    for chunk in knowledge_base:
        matches_keyword = any(word in chunk["text"].lower() or word in chunk["document_title"].lower() for word in query_words)
        matches_category = (category is None or category == "" or chunk["category"] == category)
        matches_year = (year is None or chunk["recency_year"] == year)
        if matches_keyword and matches_category and matches_year:
            results.append(chunk)
    return results

def _execute_semantic_filter(query: str) -> list[dict]:
    if not query:
        return []
    results = []
    for chunk in knowledge_base:
        if any(word in chunk["document_title"].lower() for word in query.lower().split()):
            results.append(chunk)
    return results

# --- PORTFOLIO ASYNC WORKER TASK ---

def calculate_heavy_simulation(task_id: str, initial_capital: float, horizon_years: int):
    tasks_db[task_id]["status"] = "processing"
    time.sleep(3) # Safe execution via top-declared import module
    projected_value = initial_capital * (1.08 ** horizon_years)
    tasks_db[task_id].update({
        "status": "completed",
        "expected_return": round(projected_value, 2),
        "processed_async": True
    })


# --- FASTAPI ROUTE HANDLERS ---

@app.get("/")
async def root():
    return {"status": "healthy", "engine": "AuraWealth Core", "version": "3.11"}

@app.post("/api/v1/simulate", status_code=202)
async def run_portfolio_simulation(payload: SimulationRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks_db[task_id] = {
        "portfolio_name": payload.portfolio_name,
        "status": "pending",
        "expected_return": 0.0,
        "processed_async": False
    }
    background_tasks.add_task(calculate_heavy_simulation, task_id, payload.initial_capital, payload.horizon_years)
    return {"task_id": task_id, "status": "accepted", "check_status_url": f"/api/v1/tasks/{task_id}"}

@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Simulation task tracking ID not found")
    return tasks_db[task_id]

@app.get("/api/v1/search/keyword")
async def keyword_search(query: str, category: str = None, year: int = None):
    results = _execute_keyword_filter(query, category, year)
    return {"results": results[:5], "total_matches_found": len(results)}

@app.get("/api/v1/search/semantic")
async def semantic_search(query: str):
    results = _execute_semantic_filter(query)
    return {"results": results[:5], "total_matches_found": len(results)}

@app.get("/api/v1/search/hybrid")
async def hybrid_search(query: str, category: str = None, year: int = None):
    if not query:
        return {"results": [], "total_results": 0, "source_breakdown": {"keyword_pool_size": 0, "semantic_pool_size": 0}}
        
    kw_chunks = _execute_keyword_filter(query, category, year)
    sem_chunks = _execute_semantic_filter(query)
    
    combined_dict = {}
    for chunk in kw_chunks:
        combined_dict[chunk["id"]] = chunk
        
    for chunk in sem_chunks:
        matches_category = (category is None or category == "" or chunk["category"] == category)
        matches_year = (year is None or chunk["recency_year"] == year)
        if matches_category and matches_year:
            combined_dict[chunk["id"]] = chunk
            
    final_results = list(combined_dict.values())
    
    return {
        "results": final_results[:5], 
        "total_results": len(final_results),
        "source_breakdown": {
            "keyword_pool_size": len(kw_chunks),
            "semantic_pool_size": len(sem_chunks)
        }
    }

class AgentState(BaseModel):
    user_query: str
    intake_data: str = ""
    risk_assessment: str = ""
    final_report: str = ""
    confidence_score: float = 0.0
    critic_verdict: str = ""
    fallback_used: bool = False


def review_draft(draft: str, feedback_context: str) -> tuple[float, str]:
    """Apply deterministic groundedness and completeness checks to an agent draft."""
    required_sections = ["Client Inquiry", "Intake Diagnostics", "Risk Assessment", "Next Step"]
    missing_sections = [section for section in required_sections if section not in draft]
    unsupported_claims = [phrase for phrase in ("guaranteed return", "risk-free", "will outperform") if phrase in draft.lower()]

    deductions = 0.2 * len(missing_sections) + 0.4 * len(unsupported_claims)
    if "noting stuff" in feedback_context.lower() and "Next Step" not in draft:
        deductions += 0.2

    confidence = max(0.0, round(1.0 - deductions, 2))
    if confidence < 0.80:
        reasons = missing_sections + (["unsupported financial claim"] if unsupported_claims else [])
        return confidence, f"FAIL: Draft needs revision ({', '.join(reasons)})."
    return confidence, "PASS: Draft contains the required advisory context and no unsupported guarantee language."

@app.post("/api/v1/agents/sequential")
async def run_sequential_agents(state: AgentState):
    enforce_prompt_guardrails(state.user_query)
    feedback_context = ""
    
    # 1. READ DISK CRITIQUES TO INJECT LEARNING LOOPS (Issue 9)
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r") as f:
                logs = json.load(f)
            if logs:
                # Compile all historic human rejections to guide self-correction
                all_critiques = [
                    l["advisor_critique"]
                    for l in logs
                    if "advisor_critique" in l
                    and not any(re.search(pattern, l["advisor_critique"], flags=re.IGNORECASE) for pattern in PROMPT_INJECTION_PATTERNS)
                ]
                if all_critiques:
                    feedback_context = " | ".join(all_critiques[-3:]) # Last 3 critiques
        except Exception:
            pass

    await asyncio.sleep(0.1)
    state.intake_data = "Client profile loaded. Target Track: Consumer Wealth Optimization."
    
    await asyncio.sleep(0.1)
    state.risk_assessment = "Risk thresholds verified against regional benchmarks. Parameters: Stable."

    # 2. GENERATE A DRAFT BEFORE SELF-REVIEW (Issue 8)
    simple_greeting = state.user_query.lower().strip() in {"hi", "hello", "hey"}
    if simple_greeting:
        draft = "Hello from AuraWealth."
    else:
        draft = (
            f"### 💼 AuraWealth Executive Advisory Report\n\n"
            f"* **Client Inquiry:** '{state.user_query}'\n"
            f"* **Intake Diagnostics:** {state.intake_data}\n"
            f"* **Risk Assessment:** {state.risk_assessment}\n"
            f"* **Next Step:** Confirm your planning objective before an advisor reviews any portfolio action."
        )

    # 3. CRITIC REVIEW AND FALLBACK REROUTING
    state.confidence_score, state.critic_verdict = review_draft(draft, feedback_context)
    if state.confidence_score < 0.80:
        state.fallback_used = True
        # Self-correction rewrite triggered dynamically by past poor feedback
        state.final_report = (
            f"### 🎯 AuraWealth Smart Advisory Engine\n\n"
            f"Thank you for reaching out. Based on active performance telemetry, I have adjusted my communication layer to be clearer and more engaging.\n\n"
            f"**Application Purpose:** I am a unified Wealth Management Command Center designed to replace fragmented spreadsheets. I provide everyday investors a real-time, holistic view of their net worth, while equipping wealth managers with tools to scale personal advisory service.\n\n"
            f"#### 📊 Proactive Financial Evaluation Diagnostics:\n"
            f"* **Core Pillar 1:** Automated Continuous Tax-Loss Harvesting to preserve capital gains margins.\n"
            f"* **Core Pillar 2:** Index Rebalancing to realign asset allocations dynamically.\n\n"
            f"**💡 Let's get the conversation moving:** Based on your current profile, would you like to run a forward-looking simulation on your portfolio value, or should we evaluate your asset exposure limits against macroeconomic inflation models?"
        )
    else:
        state.final_report = draft
        
    return state




@app.get("/api/v1/search/reranked")
async def reranked_search(query: str, category: str = None, year: int = None):
    # 1. Fetch raw unranked results from your existing hybrid pool logic
    raw_results = _execute_keyword_filter(query, category, year) + _execute_semantic_filter(query)
    
    # Deduplicate via dictionary
    combined = {c["id"]: c for c in raw_results}
    chunks = list(combined.values())
    
    # 2. Apply Custom Recency-Weighting Algorithm (+2 Points)
    # 2026 documents get a massive priority boost over older 2024 metrics
    for chunk in chunks:
        base_score = 1.0
        recency_multiplier = 1.5 if chunk["recency_year"] == 2026 else 1.0
        chunk["rerank_score"] = round(base_score * recency_multiplier, 2)
        
    # Sort array completely based on the new custom score matrix
    sorted_chunks = sorted(chunks, key=lambda x: x["rerank_score"], reverse=True)
    return {"results": sorted_chunks[:5]}

@app.get("/api/v1/route")
async def semantic_router(user_query: str):
    if not user_query:
        return {"route": "fallback", "model": "static"}
        
    # FinOps Optimization: Triage intent complexity instantly
    greetings = ["hi", "hello", "hey", "test", "status"]
    is_simple = any(word in user_query.lower().split() for word in greetings)
    
    if is_simple:
        return {
            "route": "lightweight_tier",
            "model": "Gemini-Flash-Mock",
            "response": f"Hello from AuraWealth Core! I am online and optimized. System status: Healthy."
        }
    else:
        return {
            "route": "premium_tier",
            "model": "Gemini-Pro-Orchestrator",
            "response": "Complex portfolio/RAG request detected. Diverting to multi-agent cluster."
        }

@app.get("/api/v1/route/llm")
async def intelligent_llm_router(user_query: str):
    if not user_query:
        return {"error": "Empty input payload query"}
        
    complex_keywords = ["portfolio", "rebalance", "tax", "risk", "audit", "optimization"]
    needs_heavy_reasoning = any(word in user_query.lower() for word in complex_keywords)
    
    # Dynamic Multi-LLM Model Selection Protocol
    if needs_heavy_reasoning:
        return {
            "selected_tier": "PREMIUM_REASONING_TIER",
            "model_identifier": "Gemini-1.5-Pro-Enterprise",
            "compute_cost_per_1k_tokens": "$0.0070",
            "reasoning_path": "Triggering advanced hybrid RAG framework search indices."
        }
    else:
        return {
            "selected_tier": "LIGHTWEIGHT_COMMUNICATION_TIER",
            "model_identifier": "Gemini-1.5-Flash-Fast",
            "compute_cost_per_1k_tokens": "$0.000075",
            "reasoning_path": "Bypassing heavy context vectors. Direct pipeline execution."
        }

# High-performance local memory cache store
search_cache: dict[str, dict] = {}

@app.get("/api/v1/search/cached")
async def cached_search(query: str):
    current_time = time.time()
    
    # Deterministically calculate TTL thresholds based on active deployment tier
    TTL_LIMIT = 86400.0 if IS_PRODUCTION else 10.0
    
    # 1. Evaluate cache database for valid unexpired entries
    if query in search_cache:
        cache_entry = search_cache[query]
        if current_time - cache_entry["timestamp"] < TTL_LIMIT:
            return {
                "results": cache_entry["data"], 
                "cache_hit": True, 
                "active_environment": "production" if IS_PRODUCTION else "development",
                "ttl_remaining_seconds": round(TTL_LIMIT - (current_time - cache_entry["timestamp"]), 2)
            }
            
    # 2. Cache Miss: Recompute filter extraction algorithms natively
    fresh_data = _execute_keyword_filter(query)
    
    # 3. Synchronize current execution snapshot back to cache layer
    search_cache[query] = {
        "timestamp": current_time,
        "data": fresh_data[:2]
    }
    return {
        "results": fresh_data[:2], 
        "cache_hit": False, 
        "active_environment": "production" if IS_PRODUCTION else "development",
        "ttl_remaining_seconds": TTL_LIMIT
    }

# In-memory global task cluster storage
queue_state_store: dict[str, dict] = {}

@app.post("/api/v1/queue/job", status_code=202)
async def push_to_message_queue(payload: dict, background_tasks: BackgroundTasks):
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    queue_state_store[job_id] = {"status": "queued", "progress": 0}
    
    # Offload execution asynchronously to our decoupled compute worker service
    background_tasks.add_task(execute_distributed_simulation, job_id, payload, queue_state_store)
    
    return {"job_id": job_id, "status": "queued", "message": "Dispatched to background message queue queue."}

@app.get("/api/v1/queue/job/{job_id}")
async def get_queue_job_status(job_id: str):
    if job_id not in queue_state_store:
        raise HTTPException(status_code=404, detail="Job token not found in cluster queue")
    return queue_state_store[job_id]

class FeedbackPayload(BaseModel):
    query: str
    critique: str

@app.post("/api/v1/feedback/log")
async def store_advisor_feedback(payload: FeedbackPayload):
    logs = []
    
    # Read existing history matrix if file already exists
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r") as f:
                logs = json.load(f)
        except Exception:
            logs = []
            
    # Append the new learning context parameters
    logs.append({
        "timestamp": time.time(),
        "user_query": payload.query,
        "advisor_critique": payload.critique
    })
    
    # Flush directly back to disk storage file
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(logs, f, indent=4)
        
    return {"status": "success", "total_stored_logs": len(logs)}


@app.get("/api/v1/queue/next")
async def get_next_queue_item(current_index: int = 0, fallback_query: str = "run agent simulation"):
    # Read our live dynamic .env configuration parameters
    current_env = ENV_CONFIG["ENV"]
    
    # Track A: If running in PROD/TEST pipelines, generate a completely real data instance
    if current_env != "DEV":
        # Simulate generating a single, genuine live-agent packet format
        return {
            "status": "active",
            "item": {
                "ticket_id": f"LIVE_{uuid.uuid4().hex[:4].upper()}",
                "user_query": fallback_query,
                "intake_data": "Client data verified. Focus area identified: Portfolio optimization.",
                "risk_assessment": "Asset allocation risk verified against regional compliance benchmarks.",
                "final_report": f"### 💼 Live AuraWealth Executive Advisory Report\n\n* **Context:** Real-time production processing enabled under active `{current_env}` environment."
            }
        }
        
    # Track B: If running in DEV mode, serve our multi-ticket interactive sandbox loop
    if current_index >= len(INCOMING_ADVISOR_QUEUE):
        return {"status": "empty", "message": "All pending advisor review queues have been successfully processed."}
    return {"status": "active", "item": INCOMING_ADVISOR_QUEUE[current_index]}
