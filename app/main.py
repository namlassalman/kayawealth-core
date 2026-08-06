import asyncio
import uuid
import os
import json
import time  # Properly anchored at the top of the file
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel

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
