from fastapi import APIRouter
from backend.app.builder.autonomous_max_evolution import run_once, run_loop

router = APIRouter()

@router.post("/api/autopilot/start")
def start():
    return run_loop(1000, 1)

@router.post("/api/autopilot/step")
def step():
    return run_once()
