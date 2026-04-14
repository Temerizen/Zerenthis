from fastapi import APIRouter, Body
from backend.app.engines.posting_result import run_result

router = APIRouter()

@router.post("/api/posting/result")
def record_posting_result(payload: dict = Body(...)):
    return run_result(payload)

