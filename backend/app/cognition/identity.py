import json
import os
import time
from typing import Dict, Any

IDENTITY_PATH = "backend/data/identity_state.json"
FEEDBACK_PATH = "backend/data/feedback_state.json"

DEFAULT_STATE = {
    "traits": {
        "confidence": 0.5,
        "curiosity": 0.5,
        "risk_tolerance": 0.5,
        "persistence": 0.5,
        "stability_preference": 0.5
    },
    "last_updated": None,
    "history": []
}

MAX_HISTORY = 100
DELTA = 0.02
DECAY = 0.01
CENTER = 0.5
MAX_TRAIT = 0.85
MIN_TRAIT = 0.15


def _load(path, default):
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


def _save(path, state):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _clamp(v):
    return max(MIN_TRAIT, min(MAX_TRAIT, v))


def _decay_toward_center(value):
    if value > CENTER:
        return max(CENTER, value - DECAY)
    if value < CENTER:
        return min(CENTER, value + DECAY)
    return value


def run(context: Dict[str, Any] | None = None):
    context = context or {}

    state = _load(IDENTITY_PATH, DEFAULT_STATE)
    feedback_state = _load(FEEDBACK_PATH, {"last_feedback": None})

    traits = state.get("traits", DEFAULT_STATE["traits"]).copy()
    feedback = feedback_state.get("last_feedback")

    delta_applied = {}

    # Soft balancing first
    balanced_traits = {}
    for key, value in traits.items():
        decayed = _decay_toward_center(float(value))
        balanced_traits[key] = _clamp(decayed)

    traits = balanced_traits

    if feedback:
        success = float(feedback.get("success_score", 0.5))
        efficiency = float(feedback.get("efficiency_score", 0.5))
        goal = str(feedback.get("goal", ""))

        if success > 0.65:
            traits["confidence"] = _clamp(traits["confidence"] + DELTA)
            traits["persistence"] = _clamp(traits["persistence"] + DELTA)
            delta_applied["confidence"] = round(delta_applied.get("confidence", 0.0) + DELTA, 4)
            delta_applied["persistence"] = round(delta_applied.get("persistence", 0.0) + DELTA, 4)

        if success < 0.4:
            traits["stability_preference"] = _clamp(traits["stability_preference"] + DELTA)
            delta_applied["stability_preference"] = round(delta_applied.get("stability_preference", 0.0) + DELTA, 4)

        if efficiency < 0.5:
            traits["curiosity"] = _clamp(traits["curiosity"] + DELTA)
            delta_applied["curiosity"] = round(delta_applied.get("curiosity", 0.0) + DELTA, 4)

        # When reinforcing repeatedly, slowly cool persistence if it gets too dominant
        if goal == "reinforce_path" and traits["persistence"] > 0.75:
            traits["curiosity"] = _clamp(traits["curiosity"] + 0.01)
            delta_applied["curiosity"] = round(delta_applied.get("curiosity", 0.0) + 0.01, 4)

        # If confidence grows high, add slight risk tolerance
        if traits["confidence"] > 0.7:
            traits["risk_tolerance"] = _clamp(traits["risk_tolerance"] + 0.01)
            delta_applied["risk_tolerance"] = round(delta_applied.get("risk_tolerance", 0.0) + 0.01, 4)

    entry = {
        "timestamp": time.time(),
        "traits": traits,
        "delta_applied": delta_applied
    }

    history = state.get("history", [])
    if not isinstance(history, list):
        history = []

    history.append(entry)
    history = history[-MAX_HISTORY:]

    new_state = {
        "traits": traits,
        "last_updated": time.time(),
        "history": history
    }

    _save(IDENTITY_PATH, new_state)

    return {
        "status": "identity_balanced",
        "traits": traits,
        "delta_applied": delta_applied,
        "history_length": len(history)
    }
