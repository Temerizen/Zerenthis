from __future__ import annotations

from fastapi import APIRouter, Body
from backend.app.cognition.meta_intelligence_engine import update_meta_intelligence

router = APIRouter(tags=["meta_intelligence"])


@router.post("/api/meta/run")
def run_meta(signal: dict = Body(...)):
    return update_meta_intelligence(signal)
