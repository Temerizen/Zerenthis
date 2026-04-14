from fastapi import APIRouter, Body
from .learning_engine import log_performance, rebuild_learning, get_learning
from .decision_engine import build_queue

router = APIRouter()

@router.post("/api/learning/log")
def learning_log(
    topic: str = Body(..., embed=True),
    platform: str = Body("", embed=True),
    views: int = Body(0, embed=True),
    likes: int = Body(0, embed=True),
    comments: int = Body(0, embed=True),
    shares: int = Body(0, embed=True),
    watch_time: float = Body(0.0, embed=True)
):
    row = log_performance(
        topic=topic,
        platform=platform,
        views=views,
        likes=likes,
        comments=comments,
        shares=shares,
        watch_time=watch_time
    )
    learning = rebuild_learning()
    queue = build_queue()
    return {
        "logged": row,
        "learning": learning,
        "queue_count": len(queue)
    }

@router.post("/api/learning/rebuild")
def learning_rebuild():
    learning = rebuild_learning()
    queue = build_queue()
    return {
        "learning": learning,
        "queue_count": len(queue)
    }

@router.get("/api/learning/state")
def learning_state():
    return get_learning()

