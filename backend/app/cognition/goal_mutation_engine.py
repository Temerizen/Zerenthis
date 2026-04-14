import json
import os
import time
from typing import Any, Dict

STATE_PATH = "backend/data/goal_mutation_state.json"

DEFAULT_STATE: Dict[str, Any] = {
    "history": [],
    "last_goal": "balanced_progression",
    "last_reason": "default",
    "last_updated": 0,
}

def _load() -> Dict[str, Any]:
    if not os.path.exists(STATE_PATH):
        return DEFAULT_STATE.copy()
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            merged = DEFAULT_STATE.copy()
            merged.update(data)
            return merged
    except Exception:
        pass
    return DEFAULT_STATE.copy()

def _save(data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def mutate_goal(current_goal: str, active_intent: Dict[str, Any] | None = None) -> Dict[str, Any]:
    active_intent = active_intent or {}
    state = _load()

    stagnating = bool(active_intent.get("stagnating", False))
    repeat_count = int(active_intent.get("repeat_count", 0) or 0)
    direction = active_intent.get("direction", "stay_the_course")

    new_goal = current_goal or "balanced_progression"
    goal_bias = 0.0
    reason = "maintain_goal"

    if stagnating or repeat_count >= 3:
        new_goal = "exploration_recovery"
        goal_bias = 0.15
        reason = "stagnation_detected"
    elif direction == "pivot_required":
        new_goal = "adaptive_reorientation"
        goal_bias = 0.12
        reason = "direction_pivot"
    elif direction == "stay_the_course":
        goal_bias = 0.05
        reason = "maintain_momentum"

    state["last_goal"] = new_goal
    state["last_reason"] = reason
    state["last_updated"] = time.time()

    state["history"].append({
        "timestamp": state["last_updated"],
        "from_goal": current_goal,
        "to_goal": new_goal,
        "reason": reason,
        "direction": direction,
        "repeat_count": repeat_count,
        "stagnating": stagnating,
    })

    state["history"] = state["history"][-100:]
    _save(state)

    return {
        "goal": new_goal,
        "goal_bias": goal_bias,
        "reason": reason
    }
