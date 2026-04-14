from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.builder.autonomous_builder import run_once, run_loop

router = APIRouter()

class LoopRequest(BaseModel):
    iterations: int = 5
    delay: float = 1.0

@router.post("/api/builder/auto-once")
def auto_once():
    return run_once()

@router.post("/api/builder/auto-loop")
def auto_loop(req: LoopRequest):
    return run_loop(req.iterations, req.delay)
