import json
import os
import time
from typing import Dict, Any

IDENTITY_PATH = "backend/data/identity_state.json"
REFLECTION_PATH = "backend/data/reflection_state.json"

DEFAULT_REFLECTION = {
    "last_reflection": None,
    "history": []
}

MAX_HISTORY = 50


def _load(path, default):
    if not os.path.exists(path):
        return default.copy()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return default.copy()
    except:
        return default.copy()


def _save(path, state):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def run(context: Dict[str, Any] | None = None):
    context = context or {}

    identity_state = _load(IDENTITY_PATH, {"history": []})
    reflection_state = _load(REFLECTION_PATH, DEFAULT_REFLECTION)

    history = identity_state.get("history", [])
    recent = history[-5:] if len(history) >= 5 else history

    insight = "stable"
    flags = []

    if len(recent) >= 3:
        last = recent[-1]["traits"]
        prev = recent[-2]["traits"]

        if last["persistence"] > 0.75:
            flags.append("high_persistence")

        if abs(last["confidence"] - prev["confidence"]) < 0.005:
            flags.append("low_change")

        if last["curiosity"] < 0.55:
            flags.append("low_exploration")

    # Determine insight
    if "high_persistence" in flags and "low_exploration" in flags:
        insight = "overfitting_behavior"

    elif "low_change" in flags:
        insight = "stagnation_detected"

    elif "low_exploration" in flags:
        insight = "exploration_needed"

    reflection = {
        "timestamp": time.time(),
        "insight": insight,
        "flags": flags
    }

    hist = reflection_state.get("history", [])
    if not isinstance(hist, list):
        hist = []

    hist.append(reflection)
    hist = hist[-MAX_HISTORY:]

    new_state = {
        "last_reflection": reflection,
        "history": hist
    }

    _save(REFLECTION_PATH, new_state)

    return {
        "status": "reflection_generated",
        "insight": insight,
        "flags": flags,
        "history_length": len(hist)
    }
