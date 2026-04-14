from fastapi import APIRouter
from backend.app.engines.priority_engine import build_priority
from backend.app.execution.runner import run_task

router = APIRouter(prefix="/api/decision", tags=["decision"])

@router.get("/next")
def get_next_action():
    return build_priority()

@router.post("/enqueue-next")
def enqueue_next_action():
    result = build_priority()
    next_action = result.get("next_action")

    if not next_action or not next_action.get("task"):
        return {
            "ok": False,
            "error": "no_next_action"
        }

    enqueue_result = run_task(next_action["task"])

    return {
        "ok": True,
        "decision": next_action,
        "enqueue_result": enqueue_result
    }
