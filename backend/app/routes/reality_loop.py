from fastapi import APIRouter
from backend.app.engines.reality_loop import run

router = APIRouter()

@router.post("/api/reality/loop")
def run_reality_loop():
    return run()

