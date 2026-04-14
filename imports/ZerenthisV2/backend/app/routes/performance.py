from fastapi import APIRouter
from backend.app.engines.performance_engine import leaderboard

router = APIRouter()

@router.get("/performance/leaderboard")
def get_leaderboard():
    return {"leaderboard": leaderboard()}

