from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.builder.autonomous_evolution import run_once, run_loop
from backend.app.builder.evolution_memory import stats, last_runs

router = APIRouter()

class LoopRequest(BaseModel):
    iterations: int = 5
    delay: float = 1.0

@router.post("/api/evolution/run-once")
def evo_once():
    return run_once()

@router.post("/api/evolution/run-loop")
def evo_loop(req: LoopRequest):
    return run_loop(req.iterations, req.delay)

@router.get("/api/evolution/stats")
def evo_stats():
    return stats()

@router.get("/api/evolution/recent")
def evo_recent():
    return last_runs(10)
