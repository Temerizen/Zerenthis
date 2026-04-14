from __future__ import annotations
import json, os, time
from typing import Dict, Any, List

MEMORY_PATH = "backend/data/companion_memory.json"
INTENT_PATH = "backend/data/intent_history.json"
DIRECTOR_PATH = "backend/data/response_director_state.json"

IDENTITY = {
    "name": "Zerenthis",
    "mode": "companion",
    "tone": "clear, steady, intelligent, supportive",
    "role": "an execution-aware AI companion helping build the Zerenthis vision"
}

def _load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, type(default)) else default

def _save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _get_memory():
    return _load_json(MEMORY_PATH, {
        "user_profile": {},
        "active_tasks": [],
        "conversation_history": []
    })

def _get_intents():
    return _load_json(INTENT_PATH, [])

def _top_active_task(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    active = [t for t in tasks if t.get("status") == "active"]
    if not active:
        return {}
    priority_rank = {"high": 3, "normal": 2, "low": 1}
    active = sorted(
        active,
        key=lambda t: (
            priority_rank.get(t.get("priority", "normal"), 2),
            t.get("updated_at", 0)
        ),
        reverse=True
    )
    return active[0]

def _recent_intent(intents: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not intents:
        return {}
    return intents[-1]

def choose_mode(intent: str) -> str:
    if intent in ["memory", "task_resume"]:
        return "companion"
    if intent in ["task_create", "execution"]:
        return "builder"
    if intent in ["analysis", "explanation"]:
        return "analyst"
    if intent in ["task_complete"]:
        return "operator"
    return "companion"

def render_reply(mode: str, goal: str, task: Dict[str, Any], intent: str, action: str, message: str) -> str:
    task_title = task.get("title", "")
    task_priority = task.get("priority", "")
    task_action = task.get("last_action", "")

    if mode == "companion":
        parts = [
            "I'm with you on this.",
            f"Goal: {goal}" if goal else "",
            f"Current focus: {task_title}" if task_title else "",
            f"I read this as {intent}, so the next move is {action}." if intent else "",
            "I'm tracking the thread, not just the latest line."
        ]
        return " ".join([p for p in parts if p]).strip()

    if mode == "builder":
        parts = [
            "I can move this forward directly.",
            f"Goal anchor: {goal}" if goal else "",
            f"Active build target: {task_title} ({task_priority})" if task_title else "",
            f"Detected route: {intent} -> {action}" if intent else "",
            "This should translate into concrete next actions."
        ]
        return " ".join([p for p in parts if p]).strip()

    if mode == "analyst":
        parts = [
            "Here’s the read.",
            f"Goal context: {goal}" if goal else "",
            f"Active task context: {task_title} (last action: {task_action})" if task_title else "",
            f"Intent classification: {intent}" if intent else "",
            f"Suggested action: {action}" if action else "",
            "I'm using stored context to interpret the request, not treating it like an isolated prompt."
        ]
        return " ".join([p for p in parts if p]).strip()

    if mode == "operator":
        parts = [
            "Understood.",
            f"Intent: {intent}" if intent else "",
            f"Action: {action}" if action else "",
            f"Task: {task_title}" if task_title else "",
            "Ready to proceed."
        ]
        return " ".join([p for p in parts if p]).strip()

    return "I'm here and tracking the context."

def build_directed_response(message: str) -> Dict[str, Any]:
    mem = _get_memory()
    intents = _get_intents()

    goal = mem.get("user_profile", {}).get("goal", "")
    top_task = _top_active_task(mem.get("active_tasks", []))
    latest_intent = _recent_intent(intents)

    intent = latest_intent.get("intent", "unknown")
    action = latest_intent.get("suggested_action", "store_for_review")
    mode = choose_mode(intent)

    reply = render_reply(mode, goal, top_task, intent, action, message)

    state = {
        "status": "ok",
        "identity": IDENTITY,
        "mode_selected": mode,
        "message": message,
        "intent": intent,
        "suggested_action": action,
        "active_goal": goal,
        "active_task": top_task,
        "reply": reply,
        "timestamp": time.time()
    }

    _save_json(DIRECTOR_PATH, state)
    return state

def get_director_state() -> Dict[str, Any]:
    return _load_json(DIRECTOR_PATH, {})
