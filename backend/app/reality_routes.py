from fastapi import APIRouter, Body
from backend.app.reality_engine import add_feedback, get_feedback, score_signal

router = APIRouter(tags=["reality"])

@router.post("/api/reality/feedback")
def feedback(data: dict = Body(...)):
    entry = add_feedback(data)
    entry["signal_score"] = score_signal(entry)
    return entry

@router.get("/api/reality/feedback")
def read(limit: int = 20):
    return get_feedback(limit)
