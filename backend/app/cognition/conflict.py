import json
import os
import time
from typing import Dict, Any

IDENTITY_PATH = "backend/data/identity_state.json"
REFLECTION_PATH = "backend/data/reflection_state.json"
META_PATH = "backend/data/meta_reflection_state.json"
CONFLICT_PATH = "backend/data/conflict_state.json"

DEFAULT_STATE = {
    "last_conflict": None,
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
    except:
        return default.copy()


def _save(path, state):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def run(context: Dict[str, Any] | None = None):
    context = context or {}

    identity = _load(IDENTITY_PATH, {"traits": {}})
    reflection = _load(REFLECTION_PATH, {"last_reflection": {}})
    meta = _load(META_PATH, {"last_meta": {}})

    traits = identity.get("traits", {})
    refl = reflection.get("last_reflection", {}) or {}
    meta_adj = meta.get("last_meta", {}).get("adjustment", {})

    curiosity = float(traits.get("curiosity", 0.5))
    persistence = float(traits.get("persistence", 0.5))
    stability = float(traits.get("stability_preference", 0.5))

    insight = str(refl.get("insight", "stable"))

    drives = {
        "explore": curiosity,
        "persist": persistence,
        "stabilize": stability
    }

    if insight == "overfitting_behavior":
        drives["explore"] += 0.15
        drives["persist"] -= 0.1

    # APPLY META ADJUSTMENTS
    drives["explore"] += float(meta_adj.get("explore_boost", 0.0))
    drives["persist"] -= float(meta_adj.get("persist_penalty", 0.0))

    # Clamp
    for k in drives:
        drives[k] = max(0.0, min(1.0, drives[k]))

    winner = max(drives, key=drives.get)

    conflict = {
        "timestamp": time.time(),
        "drives": drives,
        "winner": winner,
        "insight": insight,
        "meta_adjustment": meta_adj
    }

    state = _load(CONFLICT_PATH, DEFAULT_STATE)
    history = state.get("history", [])
    if not isinstance(history, list):
        history = []

    history.append(conflict)
    history = history[-MAX_HISTORY:]

    new_state = {
        "last_conflict": conflict,
        "history": history
    }

    _save(CONFLICT_PATH, new_state)

    return {
        "status": "conflict_resolved",
        "winner": winner,
        "drives": drives,
        "meta_adjustment": meta_adj,
        "history_length": len(history)
    }
