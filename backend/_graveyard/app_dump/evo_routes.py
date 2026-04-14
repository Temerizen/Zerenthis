from fastapi import APIRouter
from backend.app.evo_engine import run_engine

router = APIRouter()

@router.post("/api/evo/run")
def run():
    result = run_engine()
    return {"ok": True, "result": result}


