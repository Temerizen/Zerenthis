from fastapi import APIRouter, Body
from backend.app.engines.multi_target_manager import run

router = APIRouter()

@router.post("/api/targets/rank")
def rank_targets(payload: dict = Body(default={})):
    return run(payload)

