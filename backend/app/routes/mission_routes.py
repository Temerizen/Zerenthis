from fastapi import APIRouter
from backend.app.cognition.mission_engine import build_or_update_mission, advance_mission_progress

router = APIRouter()

@router.post("/api/mission/update")
def update_mission():
    return build_or_update_mission()

@router.post("/api/mission/advance")
def advance_mission():
    return advance_mission_progress()
