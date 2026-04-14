from fastapi import APIRouter
from backend.app.cognition.goal_generator import run_goal_generation

router = APIRouter()

@router.post("/api/goals/generate")
def generate_goals():
    return run_goal_generation()
