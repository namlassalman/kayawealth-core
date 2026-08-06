import asyncio
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="KayaWealth Core API",
    description="Asynchronous backend engines for portfolio optimization",
    version="1.0.0"
)

class SimulationRequest(BaseModel):
    portfolio_name: str
    initial_capital: float
    horizon_years: int

class SimulationResponse(BaseModel):
    portfolio_name: str
    status: str
    expected_return: float
    processed_async: bool

@app.get("/")
async def root():
    return {"status": "healthy", "engine": "KayaWealth Core", "version": "3.11"}

@app.post("/api/v1/simulate", response_model=SimulationResponse)
async def run_portfolio_simulation(payload: SimulationRequest):
    # Simulating an asynchronous, non-blocking I/O or heavy math operation
    await asyncio.sleep(0.5) 
    
    projected_value = payload.initial_capital * (1.08 ** payload.horizon_years)
    
    return SimulationResponse(
        portfolio_name=payload.portfolio_name,
        status="completed",
        expected_return=round(projected_value, 2),
        processed_async=True
    )
