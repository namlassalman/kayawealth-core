import asyncio
import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import os
import json

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

# Direct worker function executing outside the main request-response thread loop
def calculate_heavy_simulation(task_id: str, initial_capital: float, horizon_years: int):
    tasks_db[task_id]["status"] = "processing"
    
    # Simulate non-blocking heavy math or API roundtrips
    import time
    time.sleep(3) 
    
    projected_value = initial_capital * (1.08 ** horizon_years)
    
    tasks_db[task_id].update({
        "status": "completed",
        "expected_return": round(projected_value, 2),
        "processed_async": True
    })

@app.get("/")
async def root():
    return {"status": "healthy", "engine": "AuraWealth Core", "version": "3.11"}

@app.post("/api/v1/simulate", status_code=202)
async def run_portfolio_simulation(payload: SimulationRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    
    # Initialize the tracking state
    tasks_db[task_id] = {
        "portfolio_name": payload.portfolio_name,
        "status": "pending",
        "expected_return": 0.0,
        "processed_async": False
    }
    
    # Delegate execution directly to the background worker loop
    background_tasks.add_task(
        calculate_heavy_simulation, 
        task_id, 
        payload.initial_capital, 
        payload.horizon_years
    )
    
    # Return instantaneous 202 Accepted status payload
    return {"task_id": task_id, "status": "accepted", "check_status_url": f"/api/v1/tasks/{task_id}"}

@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Simulation task tracking ID not found")
    return tasks_db[task_id]


@app.get("/api/v1/search/keyword")
async def keyword_search(query: str):
    if not query:
        return {"results": []}
        
    results = []
    query_words = query.lower().split()
    
    # Simple, deterministic keyword scanning across all 1,000 chunks
    for chunk in knowledge_base:
        # Match if any word in the user query hits the text or document title
        if any(word in chunk["text"].lower() or word in chunk["document_title"].lower() for word in query_words):
            results.append(chunk)
            
    # Return the top 5 most relevant document matches
    return {"results": results[:5], "total_matches_found": len(results)}
