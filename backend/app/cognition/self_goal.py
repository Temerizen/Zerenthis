import json
import os
import time
from typing import Dict, Any

IDENTITY_PATH = "backend/data/identity_state.json"
REFLECTION_PATH = "backend/data/reflection_state.json"
META_PATH = "backend/data/meta_reflection_state.json"
NARRATIVE_PATH = "backend/data/narrative_state.json"
SELF_GOAL_PATH = "backend/data/self_goal_state.json"

DEFAULT_STATE = {
    "active_goal": None,
    "history": []
}

MAX_HISTORY = 100


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


def _choose_goal(traits, reflection, meta, narrative):
    confidence = traits.get("confidence", 0.5)
    curiosity = traits.get("curiosity", 0.5)
    persistence = traits.get("persistence", 0.5)

    insight = str(reflection.get("insight", ""))
    meta_insight = str(meta.get("insight", ""))

    # Decision logic (simple but powerful base)
    if "overfitting" in insight or "low_exploration" in str(reflection.get("flags", [])):
        return "increase_exploration"

    if "stagnation" in insight:
        return "introduce_variation"

    if meta_insight == "over_persistence_detected":
        return "rebalance_behavior"

    if curiosity > persistence:
        return "expand_capability"

    if persistence >= curiosity:
        return "optimize_and_scale"

    return "maintain_stability"


def run(context: Dict[str, Any] | None = None):
    context = context or {}

    identity = _load(IDENTITY_PATH, {"traits": {}})
    reflection = _load(REFLECTION_PATH, {"last_reflection": {}})
    meta = _load(META_PATH, {"last_meta": {}})
    narrative = _load(NARRATIVE_PATH, {"last_narrative": {}})
    state = _load(SELF_GOAL_PATH, DEFAULT_STATE)

    traits = identity.get("traits", {})
    last_reflection = reflection.get("last_reflection", {}) or {}
    last_meta = meta.get("last_meta", {}) or {}
    last_narrative = narrative.get("last_narrative", {}) or {}

    chosen_goal = _choose_goal(traits, last_reflection, last_meta, last_narrative)

    entry = {
        "timestamp": time.time(),
        "goal": chosen_goal,
        "traits_snapshot": traits
    }

    history = state.get("history", [])
    if not isinstance(history, list):
        history = []

    history.append(entry)
    history = history[-MAX_HISTORY:]

    new_state = {
        "active_goal": chosen_goal,
        "history": history
    }

    _save(SELF_GOAL_PATH, new_state)

    return {
        "status": "self_goal_selected",
        "active_goal": chosen_goal,
        "history_length": len(history)
    }
