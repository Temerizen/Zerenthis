from fastapi import APIRouter, Body
from backend.app.engines.signal_simulator import run

router = APIRouter()

@router.post("/api/simulate/signal")
def simulate_signal(payload: dict = Body(default={})):
    return run(payload)

