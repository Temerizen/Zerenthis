from fastapi import APIRouter, Body
from backend.app.engines.queue_manager import run

router = APIRouter()

@router.post("/api/posting/plan")
def posting_plan(payload: dict = Body(default={})):
    return run(payload)
