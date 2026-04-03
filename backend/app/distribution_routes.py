from fastapi import APIRouter, Body
from backend.app.distribution_engine import build_distribution_package, enqueue, get_queue, mark_posted

router = APIRouter(tags=["distribution"])

@router.post("/api/distribution/build")
def build(data: dict = Body(...)):
    return build_distribution_package(
        data.get("topic"),
        data.get("buyer"),
        data.get("promise"),
        data.get("niche"),
        data.get("script"),
        data.get("variants", [])
    )

@router.post("/api/distribution/queue")
def queue(data: dict = Body(...)):
    return enqueue(data)

@router.get("/api/distribution/queue")
def read_queue(limit: int = 10):
    return get_queue(limit)

@router.post("/api/distribution/posted")
def posted(data: dict = Body(...)):
    return mark_posted(data.get("id"))
