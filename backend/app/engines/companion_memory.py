from __future__ import annotations
import json, os, time
from typing import Dict, Any

MEMORY_PATH = "backend/data/companion_memory.json"

def _load():
    if not os.path.exists(MEMORY_PATH):
        return {
            "user_profile": {},
            "active_tasks": [],
            "conversation_history": []
        }
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data):
    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def remember(message: str):
    mem = _load()

    mem["conversation_history"].append({
        "message": message,
        "timestamp": time.time()
    })

    # keep memory trimmed
    mem["conversation_history"] = mem["conversation_history"][-50:]

    _save(mem)

    return {"status": "remembered"}

def set_goal(goal: str):
    mem = _load()
    mem["user_profile"]["goal"] = goal
    _save(mem)
    return {"status": "goal_saved", "goal": goal}

def get_memory():
    return _load()
