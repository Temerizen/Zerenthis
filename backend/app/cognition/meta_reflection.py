import json
import os
import time
from typing import Dict, Any

CONFLICT_PATH = "backend/data/conflict_state.json"
META_PATH = "backend/data/meta_reflection_state.json"

DEFAULT_STATE = {
    "last_meta": None,
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

    conflict_state = _load(CONFLICT_PATH, {"history": []})
    history = conflict_state.get("history", [])

    if not history or len(history) < 5:
        return {"status": "insufficient_data"}

    recent = history[-5:]

    winners = [c.get("winner") for c in recent if isinstance(c, dict)]
    persist_count = winners.count("persist")
    explore_count = winners.count("explore")

    adjustment = {
        "explore_boost": 0.0,
        "persist_penalty": 0.0
    }

    insight = "balanced"

    if persist_count >= 4:
        adjustment["explore_boost"] = 0.15
        adjustment["persist_penalty"] = 0.1
        insight = "over_persistence_detected"

    elif explore_count >= 4:
        adjustment["persist_penalty"] = -0.1
        insight = "over_exploration_detected"

    meta = {
        "timestamp": time.time(),
        "insight": insight,
        "adjustment": adjustment,
        "recent_winners": winners
    }

    state = _load(META_PATH, DEFAULT_STATE)
    hist = state.get("history", [])
    if not isinstance(hist, list):
        hist = []

    hist.append(meta)
    hist = hist[-MAX_HISTORY:]

    new_state = {
        "last_meta": meta,
        "history": hist
    }

    _save(META_PATH, new_state)

    return {
        "status": "meta_reflection_complete",
        "insight": insight,
        "adjustment": adjustment,
        "history_length": len(hist)
    }
