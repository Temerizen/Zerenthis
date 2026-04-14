from fastapi import APIRouter
from backend.app.cognition.execution_memory import record_execution
from backend.app.cognition.feedback_engine import apply_feedback

router = APIRouter()

@router.post("/api/memory/record")
def record():
    return record_execution()

@router.post("/api/feedback/apply")
def feedback():
    return apply_feedback()
