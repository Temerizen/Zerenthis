from fastapi import APIRouter
from backend.app.engines.phase_lock import run

router = APIRouter()

@router.post("/api/phase/lock")
def phase_lock():
    return run()

