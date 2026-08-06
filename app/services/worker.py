import time

# Simulated decoupled compute node (Like an AWS Lambda worker)
def execute_distributed_simulation(task_id: str, payload: dict, state_store: dict):
    state_store[task_id] = {"status": "processing", "progress": 0}
    
    # Simulate heavy distributed processing stages
    time.sleep(2)
    state_store[task_id] = {"status": "processing", "progress": 50}
    time.sleep(2)
    
    projected = payload.get("initial_capital", 10000) * (1.08 ** payload.get("horizon_years", 10))
    
    state_store[task_id] = {
        "status": "completed",
        "progress": 100,
        "result": round(projected, 2),
        "engine_node": "lambda-worker-node-alpha"
    }
