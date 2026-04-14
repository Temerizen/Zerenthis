from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.core.control_core import read_control_state, resolve_topic, set_active_topic

router = APIRouter(prefix="/api/control", tags=["control"])

class TopicRequest(BaseModel):
    topic: str | None = None

@router.get("/state")
def control_state():
    return read_control_state()

@router.post("/topic")
def control_set_topic(payload: TopicRequest):
    topic = resolve_topic(payload.topic)
    state = set_active_topic(topic)
    return {
        "status": "topic_locked",
        "topic": topic,
        "state": state
    }
