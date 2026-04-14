from fastapi import APIRouter, Body
from backend.app.engines.reality_loop_auto import run

router = APIRouter()

@router.post("/api/reality/auto-loop")
def run_reality_auto_loop(payload: dict = Body(default={})):
    return run(payload)

