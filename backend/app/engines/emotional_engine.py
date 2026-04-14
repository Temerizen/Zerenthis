from __future__ import annotations
import json, os, time, random
from typing import Dict, Any
from backend.app.engines.reflection_engine import inject_reflection

MEMORY_PATH = "backend/data/companion_memory.json"
INTENT_PATH = "backend/data/intent_history.json"
STATE_PATH = "backend/data/emotional_state.json"

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

def _clean_text(text: str) -> str:
    if not text:
        return ""
    replacements = {
        "â": "'",
        "â": '"',
        "â": '"'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def _get_memory():
    return _load_json(MEMORY_PATH, {
        "user_profile": {},
        "active_tasks": []
    })

def _get_intent():
    intents = _load_json(INTENT_PATH, [])
    return intents[-1] if intents else {}

def emotional_opening(intent: str) -> str:
    pool = {
        "analysis": [
            "Alright, let's look at this properly.",
            "There's something real in that question.",
            "Good catch. Let's break it down."
        ],
        "task_create": [
            "That's a solid move.",
            "Yeah, that should exist.",
            "Let's lock that in."
        ],
        "memory": [
            "Got it, I'm holding onto that.",
            "That matters, I'll keep it."
        ],
        "execution": [
            "We can push that forward.",
            "That's actionable."
        ],
        "default": [
            "I'm here with you.",
            "Let's keep moving."
        ]
    }
    return random.choice(pool.get(intent, pool["default"]))

def build_emotional_reply(message: str) -> Dict[str, Any]:
    mem = _get_memory()
    intent_data = _get_intent()

    goal = mem.get("user_profile", {}).get("goal", "")
    tasks = mem.get("active_tasks", [])
    active = next((t for t in tasks if t.get("status") == "active"), {})

    intent = intent_data.get("intent", "unknown")
    action = intent_data.get("suggested_action", "none")

    opening = emotional_opening(intent)
    body_parts = []

    if goal:
        body_parts.append(f"You're still aiming at: {goal}.")

    if active:
        body_parts.append(
            f"Right now you're focused on '{active.get('title')}' and it's still active."
        )

    if intent != "unknown":
        body_parts.append(
            f"This comes through as {intent}, so the natural move is {action}."
        )

    closing_pool = [
        "I'm following the thread with you.",
        "This is building, not resetting.",
        "Nothing here is isolated, it all connects."
    ]

    reply = " ".join([
        opening,
        " ".join(body_parts),
        random.choice(closing_pool)
    ]).strip()

    reply = _clean_text(reply)
    reply = inject_reflection(reply, intent)

    state = {
        "status": "ok",
        "intent": intent,
        "reply": reply,
        "timestamp": time.time()
    }

    _save_json(STATE_PATH, state)
    return state

def get_emotional_state():
    return _load_json(STATE_PATH, {})
