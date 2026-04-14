from fastapi import APIRouter, Body
from backend.app.execution.runner import execute_all, load_log, run_task

router = APIRouter(prefix="/api/execution", tags=["execution"])

@router.post("/enqueue")
def enqueue_system(payload: dict = Body(...)):
    task = payload.get("task")
    if not task:
        return {"ok": False, "error": "missing_task"}
    result = run_task(task)
    return {"ok": True, "result": result}

@router.post("/run")
def run_systems():
    results = execute_all(limit=10)
    return {"ok": True, "results": results}

@router.get("/logs")
def get_logs():
    return {"logs": load_log()}
