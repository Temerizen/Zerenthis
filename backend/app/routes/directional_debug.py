from fastapi import APIRouter
from backend.app.core.directional_bias import compute_directional_score, choose_best_goal

router = APIRouter(prefix="/api/directional", tags=["directional"])

@router.get("/test")
def directional_test():
    goals = [
        {"goal_id": "reduce_revenue_scan", "score": 0.92},
        {"goal_id": "initiate_recovery_mode", "score": 0.90},
        {"goal_id": "improve_tool_strategy", "score": 0.70},
    ]
    return choose_best_goal(goals, system_state="stable")
