from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.builder.autonomous_max_evolution import run_once, run_loop

router = APIRouter()

class LoopRequest(BaseModel):
    iterations: int = 5
    delay: float = 1.0

@router.post("/api/max-evolution/run-once")
def max_evo_once():
    return run_once()

@router.post("/api/max-evolution/run-loop")
def max_evo_loop(req: LoopRequest):
    return run_loop(req.iterations, req.delay)
