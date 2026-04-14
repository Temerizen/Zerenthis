from __future__ import annotations

from fastapi import APIRouter, Body
from backend.app.cognition.self_model_engine import update_self_model, get_self_model

router = APIRouter(tags=["self_model"])


@router.post("/api/self/update")
def self_update(payload: dict = Body(...)):
    return update_self_model(payload)


@router.get("/api/self/state")
def self_state():
    return get_self_model()
