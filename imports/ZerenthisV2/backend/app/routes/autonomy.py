from fastapi import APIRouter
from backend.app.engines.autonomy_engine import run_autonomy

router = APIRouter()

@router.post("/autonomy/run")
def run_auto(payload: dict = {}):
    iterations = int(payload.get("iterations", 5))
    delay = int(payload.get("delay", 1))
    return {
        "cycles": run_autonomy(iterations, delay),
        "count": iterations
    }

