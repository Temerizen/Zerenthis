from fastapi import APIRouter, Body
from backend.app.engines.posting_execute import run_execute

router = APIRouter()

@router.post("/api/posting/execute")
def execute_posting(payload: dict = Body(...)):
    return run_execute(payload)

