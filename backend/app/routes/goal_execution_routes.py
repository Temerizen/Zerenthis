from fastapi import APIRouter
from backend.app.cognition.goal_arbiter import select_active_goal
from backend.app.cognition.goal_executor import execute_active_goal

router = APIRouter()

@router.post("/api/goals/select")
def select_goal():
    return select_active_goal()

@router.post("/api/goals/execute")
def execute_goal():
    return execute_active_goal()
