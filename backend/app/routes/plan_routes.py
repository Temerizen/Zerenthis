from fastapi import APIRouter
from backend.app.cognition.plan_engine import build_active_plan, advance_active_plan

router = APIRouter()

@router.post("/api/plan/build")
def build_plan():
    return build_active_plan()

@router.post("/api/plan/advance")
def advance_plan():
    return advance_active_plan()
