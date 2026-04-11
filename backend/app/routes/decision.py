from fastapi import APIRouter
from app.engines import decision_engine as d

router = APIRouter(prefix="/api/decision")

@router.post("/seed")
def seed():
    return d.seed()

@router.get("/queue")
def queue():
    return d.queue()

@router.get("/next")
def next_best():
    return d.next_best()

@router.post("/feedback")
def feedback(payload: dict):
    return d.feedback(payload["idea"], payload["score"])

@router.get("/winners")
def winners():
    return d.winners()
