import json
import os
import time
from typing import Dict, Any

FEEDBACK_PATH = "backend/data/feedback_state.json"

DEFAULT_STATE = {
    "last_feedback": None,
    "history": []
}

MAX_HISTORY = 100


def _load():
    if not os.path.exists(FEEDBACK_PATH):
        return DEFAULT_STATE.copy()
    try:
        with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return DEFAULT_STATE.copy()


def _save(state):
    os.makedirs(os.path.dirname(FEEDBACK_PATH), exist_ok=True)
    with open(FEEDBACK_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _score_execution(execution: Dict[str, Any]) -> Dict[str, float]:
    steps = execution.get("steps_executed", [])
    step_count = len(steps)

    if step_count == 0:
        return {
            "success_score": 0.2,
            "efficiency_score": 0.2
        }

    if step_count <= 2:
        return {
            "success_score": 0.5,
            "efficiency_score": 0.4
        }

    if step_count <= 4:
        return {
            "success_score": 0.7,
            "efficiency_score": 0.6
        }

    return {
        "success_score": 0.9,
        "efficiency_score": 0.75
    }


def run(context: Dict[str, Any] | None = None):
    context = context or {}

    state = _load()

    execution = context.get("execution", {})
    goal = execution.get("goal", "unknown")

    scores = _score_execution(execution)

    entry = {
        "timestamp": time.time(),
        "goal": goal,
        "success_score": scores["success_score"],
        "efficiency_score": scores["efficiency_score"],
        "steps_count": len(execution.get("steps_executed", []))
    }

    history = state.get("history", [])
    history.append(entry)
    history = history[-MAX_HISTORY:]

    new_state = {
        "last_feedback": entry,
        "history": history
    }

    _save(new_state)

    return {
        "status": "feedback_recorded",
        "goal": goal,
        "scores": scores,
        "history_length": len(history)
    }
