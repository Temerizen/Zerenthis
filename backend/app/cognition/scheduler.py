from __future__ import annotations

import json
import os
import time
from typing import Any, Dict

STATE_PATH = "backend/data/scheduler_state.json"

DEFAULT_STATE: Dict[str, Any] = {
    "last_seen_task": None,
    "last_seen_goal": None,
    "tick_count": 0,
    "history": [],
}


def _safe_load(path: str, default: Any) -> Any:
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _safe_save(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def _normalize(payload: Any = None) -> Dict[str, Any]:
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, str):
        return {"task": payload}
    return {}


def get_state() -> Dict[str, Any]:
    state = _safe_load(STATE_PATH, DEFAULT_STATE.copy())
    merged = DEFAULT_STATE.copy()
    if isinstance(state, dict):
        merged.update(state)
    if not isinstance(merged.get("history"), list):
        merged["history"] = []
    return merged


def run(payload: Any = None) -> Dict[str, Any]:
    data = _normalize(payload)
    state = get_state()

    task = data.get("task")
    goal = data.get("goal")
    trigger = data.get("trigger", "scheduler_tick")

    state["last_seen_task"] = task
    state["last_seen_goal"] = goal
    state["tick_count"] = int(state.get("tick_count", 0)) + 1

    history = state.get("history", [])
    if not isinstance(history, list):
        history = []
    history.append({
        "timestamp": time.time(),
        "task": task,
        "goal": goal,
        "trigger": trigger,
    })
    state["history"] = history[-100:]

    _safe_save(STATE_PATH, state)

    return {
        "status": "scheduler_tick",
        "task": task,
        "goal": goal,
        "tick_count": state["tick_count"],
        "trigger": trigger,
    }


def update(payload: Any = None) -> Dict[str, Any]:
    return run(payload)
