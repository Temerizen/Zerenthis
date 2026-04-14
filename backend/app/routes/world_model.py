from __future__ import annotations

from fastapi import APIRouter, Body
from backend.app.cognition.world_model_engine import get_world_state, update_world_model

router = APIRouter(tags=["world_model"])


@router.post("/api/world/update")
def world_update(payload: dict = Body(...)):
    return update_world_model(payload)


@router.get("/api/world/state")
def world_state():
    return get_world_state()
