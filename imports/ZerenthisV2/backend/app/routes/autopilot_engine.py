from fastapi import APIRouter
from backend.app.engines.autopilot_engine import run

router = APIRouter()

@router.post("/api/autopilot/run")
def run_autopilot():
    return run()
