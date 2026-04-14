import json
import os
import time
from typing import Dict, Any

REFLECTION_PATH = "backend/data/reflection_state.json"
OVERRIDE_PATH = "backend/data/override_state.json"

DEFAULT_STATE = {
    "last_override": None,
    "history": []
}

MAX_HISTORY = 100


def _load(path: str, default: Dict[str, Any]) -> Dict[str, Any]:
    if not os.path.exists(path):
        return default.copy()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return default.copy()
    except Exception:
        return default.copy()


def _save(path: str, state: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def run(context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    context = context or {}

    reflection_state = _load(REFLECTION_PATH, {"last_reflection": None})
    state = _load(OVERRIDE_PATH, DEFAULT_STATE)

    reflection = reflection_state.get("last_reflection", {}) or {}
    insight = str(reflection.get("insight", "stable"))
    flags = reflection.get("flags", [])
    if not isinstance(flags, list):
        flags = []

    override = {
        "force_mode": None,
        "force_goal": None,
        "reason": "none"
    }

    if insight == "overfitting_behavior":
        override = {
            "force_mode": "explore",
            "force_goal": "expand_capability",
            "reason": "reflection_override_overfitting"
        }
    elif insight == "stagnation_detected":
        override = {
            "force_mode": "explore",
            "force_goal": "expand_capability",
            "reason": "reflection_override_stagnation"
        }
    elif insight == "exploration_needed":
        override = {
            "force_mode": "explore",
            "force_goal": "expand_capability",
            "reason": "reflection_override_low_exploration"
        }

    entry = {
        "timestamp": time.time(),
        "insight": insight,
        "flags": flags,
        "override": override
    }

    history = state.get("history", [])
    if not isinstance(history, list):
        history = []

    history.append(entry)
    history = history[-MAX_HISTORY:]

    new_state = {
        "last_override": entry,
        "history": history
    }

    _save(OVERRIDE_PATH, new_state)

    return {
        "status": "override_evaluated",
        "insight": insight,
        "override": override,
        "history_length": len(history)
    }
