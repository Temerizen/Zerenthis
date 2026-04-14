from fastapi import APIRouter
from backend.app.engines.evolution_engine import run

router = APIRouter()

@router.post("/api/evolve")
def evolve():
    return run()
