import json
import os
import time
from typing import Dict, Any

IDENTITY_PATH = "backend/data/identity_state.json"
META_PATH = "backend/data/meta_reflection_state.json"
CONFLICT_PATH = "backend/data/conflict_state.json"

MAX_HISTORY = 100
DELTA = 0.01  # smaller than before (very slow change)


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


def _clamp(v):
    return max(0.0, min(1.0, v))


def run(context: Dict[str, Any] | None = None):
    context = context or {}

    identity = _load(IDENTITY_PATH, {
        "traits": {
            "confidence": 0.5,
            "curiosity": 0.5,
            "risk_tolerance": 0.5,
            "persistence": 0.5,
            "stability_preference": 0.5
        },
        "history": []
    })

    meta = _load(META_PATH, {"last_meta": {}})
    conflict = _load(CONFLICT_PATH, {"last_conflict": {}})

    traits = identity.get("traits", {}).copy()
    meta_insight = meta.get("last_meta", {}).get("insight")
    winner = conflict.get("last_conflict", {}).get("winner")

    delta_applied = {}

    # =========================
    # RULES: VERY SLOW IDENTITY EVOLUTION
    # =========================

    if meta_insight == "over_persistence_detected":
        traits["persistence"] = _clamp(traits["persistence"] - DELTA)
        traits["curiosity"] = _clamp(traits["curiosity"] + DELTA)

        delta_applied["persistence"] = -DELTA
        delta_applied["curiosity"] = DELTA

    if winner == "explore":
        traits["curiosity"] = _clamp(traits["curiosity"] + DELTA)
        traits["risk_tolerance"] = _clamp(traits["risk_tolerance"] + DELTA)

        delta_applied["curiosity"] = delta_applied.get("curiosity", 0) + DELTA
        delta_applied["risk_tolerance"] = DELTA

    if winner == "persist":
        traits["confidence"] = _clamp(traits["confidence"] + DELTA)
        traits["persistence"] = _clamp(traits["persistence"] + DELTA)

        delta_applied["confidence"] = DELTA
        delta_applied["persistence"] = delta_applied.get("persistence", 0) + DELTA

    # =========================
    # HISTORY
    # =========================
    entry = {
        "timestamp": time.time(),
        "traits": traits,
        "delta_applied": delta_applied,
        "meta_insight": meta_insight,
        "winner": winner
    }

    history = identity.get("history", [])
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
        "status": "identity_rewritten",
        "traits": traits,
        "delta_applied": delta_applied,
        "meta_insight": meta_insight,
        "winner": winner,
        "history_length": len(history)
    }
