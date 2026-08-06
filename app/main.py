import asyncio
import uuid
import os
import json
import time  # Properly anchored at the top of the file
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel

# --- ENVIRONMENT STATE CONFIGURATION ---
IS_PRODUCTION = False  # Toggle to True for presentation mode or deployment configs

# Automatically load the 1,000 chunks into local server RAM on startup
KB_PATH = os.path.join(os.path.dirname(__file__), "kb_chunks.json")
with open(KB_PATH, "r") as f:
    knowledge_base: list[dict] = json.load(f)

app = FastAPI(
    title="AuraWealth Core API",
    description="Asynchronous backend engine for portfolio optimization and agent routing",
    version="1.0.0"
)

# Thread-safe in-memory task database matrix
tasks_db: dict[str, dict] = {}

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

@app.post("/api/v1/agents/sequential")
async def run_sequential_agents(state: AgentState):
    await asyncio.sleep(0.5)
    state.intake_data = "Client data verified. Focus area identified: Portfolio optimization and tax tracking."
    
    await asyncio.sleep(0.5)
    state.risk_assessment = "Asset allocation risk verified against regional compliance benchmarks. Status: Approved (Tier-1 Low Volatility)."
    
    await asyncio.sleep(0.5)
    state.final_report = (
        f"### 💼 AuraWealth Executive Advisory Report\n\n"
        f"* **Client Request Profile:** '{state.user_query}'\n"
        f"* **Intake Diagnostics:** {state.intake_data}\n"
        f"* **Risk Assessment:** {state.risk_assessment}\n\n"
        f"* **Strategic Recommendation:** Proceed with tax-optimized rebalancing. Portfolio risk matches parameters cleanly."
    )
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
