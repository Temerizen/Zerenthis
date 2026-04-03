from fastapi import APIRouter
from backend.app.decision_engine import build_queue, get_ranked, get_next, mark_posted

router = APIRouter()

@router.post("/api/decision/build")
def build():
    return {"queue": build_queue()}

@router.get("/api/decision/rank")
def rank():
    return get_ranked()

@router.get("/api/decision/next")
def next_item():
    return get_next()

@router.post("/api/decision/mark-posted")
def post(title: str):
    return mark_posted(title)
