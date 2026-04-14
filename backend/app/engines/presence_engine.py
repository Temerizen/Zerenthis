from __future__ import annotations
import json, os, time
from typing import Dict, Any, List

MEMORY_PATH = "backend/data/companion_memory.json"
INTENT_PATH = "backend/data/intent_history.json"
PRESENCE_PATH = "backend/data/presence_state.json"

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

def build_presence_reply(message: str) -> Dict[str, Any]:
    mem = _get_memory()
    intents = _get_intents()

    goal = mem.get("user_profile", {}).get("goal", "")
    tasks = mem.get("active_tasks", [])
    top_task = _top_active_task(tasks)
    latest_intent = _recent_intent(intents)

    intent = latest_intent.get("intent", "unknown")
    suggested_action = latest_intent.get("suggested_action", "store_for_review")

    opening = "I'm here."
    if intent == "memory":
        opening = "I've got that."
    elif intent == "task_create":
        opening = "I can anchor that as active work."
    elif intent == "task_resume":
        opening = "I can pick that thread back up."
    elif intent == "analysis":
        opening = "I can look at that directly."
    elif intent == "execution":
        opening = "I can move that forward."
    elif intent == "explanation":
        opening = "I can break that down."

    context_lines = []
    if goal:
        context_lines.append(f"Current goal: {goal}")
    if top_task:
        context_lines.append(
            f"Active focus: {top_task.get('title')} "
            f"(priority: {top_task.get('priority')}, last action: {top_task.get('last_action')})"
        )
    if intent:
        context_lines.append(f"Detected intent: {intent} -> {suggested_action}")

    response = {
        "status": "ok",
        "identity": IDENTITY,
        "message": message,
        "intent": intent,
        "suggested_action": suggested_action,
        "active_goal": goal,
        "active_task": top_task,
        "reply": " ".join([
            opening,
            " ".join(context_lines) if context_lines else "",
            "I'm tracking the thread, not just the message."
        ]).strip(),
        "timestamp": time.time()
    }

    _save_json(PRESENCE_PATH, response)
    return response

def get_presence_state() -> Dict[str, Any]:
    return _load_json(PRESENCE_PATH, {})
