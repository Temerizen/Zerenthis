from fastapi import APIRouter
from app.engines.execution_engine import run_task
from app.engines.decision_engine import next_best

router = APIRouter(prefix="/api/execution")

@router.post("/run")
def run():
    idea = next_best()
    if not idea:
        return {"error": "no ideas"}

    return run_task(idea["idea"])

