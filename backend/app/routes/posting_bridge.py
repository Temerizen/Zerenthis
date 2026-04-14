from fastapi import APIRouter, Body
from backend.app.engines.posting_bridge import run

router = APIRouter()

@router.post("/api/posting/prepare")
def prepare_posting(payload: dict = Body(default={})):
    return run(payload)

