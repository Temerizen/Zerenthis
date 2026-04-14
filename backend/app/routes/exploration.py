from __future__ import annotations

from fastapi import APIRouter, Body
from backend.app.cognition.exploration_engine import run_exploration, get_exploration_state

router = APIRouter(tags=["exploration"])


@router.post("/api/explore/run")
def explore(payload: dict = Body(...)):
    return run_exploration(payload)


@router.get("/api/explore/state")
def explore_state():
    return get_exploration_state()
