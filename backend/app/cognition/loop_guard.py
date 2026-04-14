from __future__ import annotations
import json
import os
from typing import Any, Dict

STATE_PATH = "backend/data/loop_state.json"

def _default_state() -> Dict[str, Any]:
    return {
        "last_task": None,
        "repeat_count": 0,
    }

def _load() -> Dict[str, Any]:
    if not os.path.exists(STATE_PATH):
        return _default_state()
    try:
        with open(STATE_PATH, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return _default_state()
            state = _default_state()
            state.update(data)
            return state
    except Exception:
        return _default_state()

def _save(data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _extract_task(task_or_mission: Any) -> str:
    if isinstance(task_or_mission, str):
        return task_or_mission
    if isinstance(task_or_mission, dict):
        mission = task_or_mission.get("mission", {}) if isinstance(task_or_mission.get("mission", {}), dict) else {}
        return str(
            task_or_mission.get("task")
            or mission.get("last_executed_task")
            or mission.get("focus_task")
            or "unknown"
        )
    return "unknown"

def detect_loop(task_or_mission: Any) -> Dict[str, Any]:
    task = _extract_task(task_or_mission)
    state = _load()

    if state.get("last_task") == task:
        state["repeat_count"] = int(state.get("repeat_count", 0)) + 1
    else:
        state["repeat_count"] = 0

    state["last_task"] = task
    _save(state)

    return {
        "status": "ok",
        "task": task,
        "repeat_count": state["repeat_count"],
        "looping": state["repeat_count"] >= 3,
    }

def enforce_reality(execution_result: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(execution_result, dict) and execution_result.get("status") == "execution_complete":
        execution_result["confidence"] = 0.6
        execution_result["note"] = "forced_reality_check"
    return execution_result

def should_force_builder(task_or_mission: Any) -> bool:
    return bool(detect_loop(task_or_mission).get("looping", False))
