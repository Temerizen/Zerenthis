import json
import os
import time
from typing import Dict, Any

DRIVE_PATH = "backend/data/drive_state.json"
INFLUENCE_PATH = "backend/data/drive_influence_state.json"

DEFAULT_STATE = {
    "version": 1,
    "last_updated": None,
    "last_influence": None,
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


def _save(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _influence_from_drive(active_drive: str) -> Dict[str, Any]:
    active_drive = str(active_drive or "balance").strip().lower()

    if active_drive == "explore":
        return {
            "decision_bias": "novelty",
            "goal_bias": "expansion",
            "planning_bias": "breadth",
            "execution_bias": "adaptive"
        }

    if active_drive == "stabilize":
        return {
            "decision_bias": "safety",
            "goal_bias": "continuity",
            "planning_bias": "constraint",
            "execution_bias": "conservative"
        }

    if active_drive == "persist":
        return {
            "decision_bias": "consistency",
            "goal_bias": "long_horizon",
            "planning_bias": "depth",
            "execution_bias": "durable"
        }

    return {
        "decision_bias": "balanced",
        "goal_bias": "balanced",
        "planning_bias": "balanced",
        "execution_bias": "balanced"
    }


def run(context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    context = context or {}

    drive_state = _load(DRIVE_PATH, {"active_drive": "balance"})
    state = _load(INFLUENCE_PATH, DEFAULT_STATE)

    active_drive = drive_state.get("active_drive", "balance")
    influence = _influence_from_drive(active_drive)

    entry = {
        "timestamp": time.time(),
        "active_drive": active_drive,
        "influence": influence
    }

    history = state.get("history", [])
    if not isinstance(history, list):
        history = []

    history.append(entry)
    history = history[-MAX_HISTORY:]

    new_state = state.copy()
    new_state["last_updated"] = time.time()
    new_state["last_influence"] = entry
    new_state["history"] = history

    _save(INFLUENCE_PATH, new_state)

    return {
        "status": "drive_influence_applied",
        "active_drive": active_drive,
        "influence": influence,
        "history_length": len(history)
    }
