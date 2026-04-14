from fastapi import APIRouter
from backend.app.cognition.meta_intelligence_engine import update_meta_intelligence

router = APIRouter()

@router.post("/api/meta/run")
def run_meta(signal: dict):
    return update_meta_intelligence(signal)
