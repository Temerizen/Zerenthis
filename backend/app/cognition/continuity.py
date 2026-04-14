from __future__ import annotations

import json
import os
import time
from typing import Any, Dict

STATE_PATH = "backend/data/continuity_state.json"

DEFAULT_STATE: Dict[str, Any] = {
    "active": False,
    "interval_seconds": 3.0,
    "max_errors": 5,
    "max_cycles": None,
    "cycles_completed": 0,
    "consecutive_errors": 0,
    "last_error": None,
    "last_started_at": None,
    "last_cycle_started_at": None,
    "last_cycle_finished_at": None,
    "last_stop_reason": "not_started",
    "last_continue_reason": "idle",
    "continue_bias": 0.60,
    "manual_hold": False,
    "session_id": None,
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


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def get_state() -> Dict[str, Any]:
    state = _safe_load(STATE_PATH, DEFAULT_STATE.copy())
    merged = DEFAULT_STATE.copy()
    if isinstance(state, dict):
        merged.update(state)
    return merged


def save_state(state: Dict[str, Any]) -> Dict[str, Any]:
    _safe_save(STATE_PATH, state)
    return state


def update_state(patch: Dict[str, Any]) -> Dict[str, Any]:
    state = get_state()
    state.update(patch or {})
    return save_state(state)


def start(
    interval_seconds: float = 3.0,
    max_errors: int = 5,
    max_cycles: int | None = None,
    reason: str = "manual_start",
) -> Dict[str, Any]:
    interval_seconds = max(1.0, min(float(interval_seconds), 300.0))
    max_errors = max(1, min(int(max_errors), 100))
    if max_cycles is not None:
        max_cycles = max(1, int(max_cycles))

    state = get_state()
    state["active"] = True
    state["interval_seconds"] = interval_seconds
    state["max_errors"] = max_errors
    state["max_cycles"] = max_cycles
    state["consecutive_errors"] = 0
    state["last_error"] = None
    state["last_started_at"] = time.time()
    state["last_stop_reason"] = reason
    state["manual_hold"] = False
    state["session_id"] = int(time.time())
    return save_state(state)


def stop(reason: str = "manual_stop") -> Dict[str, Any]:
    state = get_state()
    state["active"] = False
    state["last_stop_reason"] = reason
    state["manual_hold"] = True if reason == "manual_hold" else False
    return save_state(state)


def clear_hold() -> Dict[str, Any]:
    state = get_state()
    state["manual_hold"] = False
    return save_state(state)


def record_cycle_start() -> Dict[str, Any]:
    state = get_state()
    state["last_cycle_started_at"] = time.time()
    return save_state(state)


def record_cycle_result(should_continue: bool, reason: str = "continue") -> Dict[str, Any]:
    state = get_state()
    state["last_cycle_finished_at"] = time.time()
    state["cycles_completed"] = int(state.get("cycles_completed", 0)) + 1
    state["consecutive_errors"] = 0
    state["last_continue_reason"] = reason
    if not should_continue:
        state["active"] = False
        state["last_stop_reason"] = reason
    if state.get("max_cycles") is not None and state["cycles_completed"] >= int(state["max_cycles"]):
        state["active"] = False
        state["last_stop_reason"] = "max_cycles_reached"
    return save_state(state)


def record_error(error_text: str) -> Dict[str, Any]:
    state = get_state()
    state["consecutive_errors"] = int(state.get("consecutive_errors", 0)) + 1
    state["last_error"] = str(error_text)
    state["last_cycle_finished_at"] = time.time()
    if state["consecutive_errors"] >= int(state.get("max_errors", 5)):
        state["active"] = False
        state["last_stop_reason"] = "error_clamp_triggered"
    return save_state(state)


def should_continue(
    active_mission: Dict[str, Any] | None = None,
    goal_state: Dict[str, Any] | None = None,
    reflection_state: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    state = get_state()

    if not state.get("active", False):
        return {"should_continue": False, "reason": "engine_inactive"}

    if state.get("manual_hold", False):
        return {"should_continue": False, "reason": "manual_hold"}

    if state.get("max_cycles") is not None and int(state.get("cycles_completed", 0)) >= int(state["max_cycles"]):
        return {"should_continue": False, "reason": "max_cycles_reached"}

    active_mission = active_mission or {}
    goal_state = goal_state or {}
    reflection_state = reflection_state or {}

    mission_status = str(active_mission.get("status", "")).lower()
    commitment = _num(goal_state.get("commitment", goal_state.get("persistence", 0.0)))
    pressure = _num(reflection_state.get("pressure", 0.0))
    confidence = _num(reflection_state.get("confidence", state.get("continue_bias", 0.60)))
    pending_tasks = active_mission.get("blocked_tasks") or active_mission.get("pending_tasks") or []
    has_pending_tasks = isinstance(pending_tasks, list) and len(pending_tasks) > 0

    if mission_status == "active":
        return {"should_continue": True, "reason": "active_mission"}

    if has_pending_tasks:
        return {"should_continue": True, "reason": "pending_tasks"}

    if commitment >= 0.35:
        return {"should_continue": True, "reason": "goal_commitment"}

    if pressure >= 0.20:
        return {"should_continue": True, "reason": "reflection_pressure"}

    if confidence >= 0.55:
        return {"should_continue": True, "reason": "continuity_bias"}

    if int(state.get("cycles_completed", 0)) == 0:
        return {"should_continue": True, "reason": "bootstrap_cycle"}

    return {"should_continue": False, "reason": "no_internal_driver"}
