from fastapi import APIRouter, Body
from backend.app.engines.reality_bridge import run

router = APIRouter()

@router.post("/api/reality/ingest")
def ingest_reality_signal(payload: dict = Body(...)):
    return run(payload)
