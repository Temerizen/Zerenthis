from fastapi import APIRouter
from backend.app.engines.champion_engine import run

router = APIRouter()

@router.post("/api/champion/run")
def champion_cycle():
    return run()

