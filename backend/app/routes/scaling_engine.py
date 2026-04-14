from fastapi import APIRouter
from backend.app.engines.scaling_engine import run

router = APIRouter()

@router.post("/api/scale/run")
def run_scaling():
    return run()

