from fastapi import APIRouter
from backend.app.cognition.initiative_engine import build_initiative_goals

router = APIRouter()

@router.post("/api/initiative/generate")
def generate_initiative():
    return build_initiative_goals()
