from fastapi import APIRouter
from backend.app.core.openai_client import chat
from backend.app.agents.builder import create_plan
from backend.app.agents.watcher import audit
from backend.app.core.tasks import create_task

router = APIRouter()

@router.post("/api/founder/chat")
def founder_chat(payload: dict):
    user_input = payload.get("message", "")

    plan = create_plan(user_input)
    task = create_task(plan)
    system_audit = audit()

    ai_response = chat([
        {"role": "system", "content": "You are Zerenthis Orchestrator. Convert founder intent into execution strategy."},
        {"role": "user", "content": user_input}
    ])

    return {
        "response": ai_response,
        "plan": plan,
        "task": task,
        "system": system_audit
    }

