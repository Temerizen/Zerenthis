from fastapi import APIRouter
from backend.app.execution.runner import execute_all, load_log

router = APIRouter(prefix="/api/execution", tags=["execution"])

@router.post("/run")
def run_systems():
    results = execute_all(limit=10)
    return {"ok": True, "results": results}

@router.get("/logs")
def get_logs():
    return {"logs": load_log()}
