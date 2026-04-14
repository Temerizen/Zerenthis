from __future__ import annotations
import json, os, time, re
from typing import Dict, Any

INTENT_PATH = "backend/data/intent_history.json"

def _load():
    if not os.path.exists(INTENT_PATH):
        return []
    with open(INTENT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []

def _save(data):
    os.makedirs(os.path.dirname(INTENT_PATH), exist_ok=True)
    with open(INTENT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def classify_intent(message: str) -> Dict[str, Any]:
    text = (message or "").strip()
    lower = text.lower()

    intent = "unknown"
    confidence = 0.5
    suggested_action = "store_for_review"

    if any(x in lower for x in ["remember this", "save this", "note this", "store this"]):
        intent = "memory"
        confidence = 0.95
        suggested_action = "write_memory"

    elif any(x in lower for x in ["create task", "add task", "new task", "track this task"]):
        intent = "task_create"
        confidence = 0.95
        suggested_action = "create_task"

    elif any(x in lower for x in ["resume task", "continue task", "continue this", "pick this back up"]):
        intent = "task_resume"
        confidence = 0.9
        suggested_action = "resume_task"

    elif any(x in lower for x in ["complete task", "finish task", "mark done", "mark complete"]):
        intent = "task_complete"
        confidence = 0.9
        suggested_action = "complete_task"

    elif any(x in lower for x in ["build", "make", "implement", "install", "create", "do this"]):
        intent = "execution"
        confidence = 0.8
        suggested_action = "execute_or_plan"

    elif any(x in lower for x in ["analyze", "diagnose", "inspect", "review", "check"]):
        intent = "analysis"
        confidence = 0.85
        suggested_action = "analyze_request"

    elif any(x in lower for x in ["what is", "explain", "how does", "why does", "how many"]):
        intent = "explanation"
        confidence = 0.85
        suggested_action = "explain_or_answer"

    # extra continuation signal
    if re.search(r"\b(next|continue|go on)\b", lower):
        if intent == "unknown":
            intent = "task_resume"
            confidence = 0.75
            suggested_action = "resume_context"

    result = {
        "message": text,
        "intent": intent,
        "confidence": confidence,
        "suggested_action": suggested_action,
        "timestamp": time.time()
    }

    history = _load()
    history.append(result)
    history = history[-100:]
    _save(history)

    return result

def get_intent_history():
    history = _load()
    return {
        "status": "ok",
        "count": len(history),
        "history": history[-20:]
    }
