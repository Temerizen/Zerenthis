import json
import os
import time
from typing import Dict, Any

IDENTITY_PATH = "backend/data/identity_state.json"
REFLECTION_PATH = "backend/data/reflection_state.json"
META_PATH = "backend/data/meta_reflection_state.json"
CONFLICT_PATH = "backend/data/conflict_state.json"
NARRATIVE_PATH = "backend/data/narrative_state.json"

DEFAULT_STATE = {
    "last_narrative": None,
    "history": []
}

MAX_HISTORY = 100


def _load(path: str, default: Dict[str, Any]) -> Dict[str, Any]:
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


def _save(path: str, state: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _dominant_trait(traits: Dict[str, Any]) -> str:
    if not isinstance(traits, dict) or not traits:
        return "unknown"
    return max(traits, key=lambda k: float(traits.get(k, 0.0)))


def run(context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    context = context or {}

    identity = _load(IDENTITY_PATH, {"traits": {}})
    reflection = _load(REFLECTION_PATH, {"last_reflection": {}})
    meta = _load(META_PATH, {"last_meta": {}})
    conflict = _load(CONFLICT_PATH, {"last_conflict": {}})
    state = _load(NARRATIVE_PATH, DEFAULT_STATE)

    traits = identity.get("traits", {})
    last_reflection = reflection.get("last_reflection", {}) or {}
    last_meta = meta.get("last_meta", {}) or {}
    last_conflict = conflict.get("last_conflict", {}) or {}

    dominant_trait = _dominant_trait(traits)
    reflection_insight = str(last_reflection.get("insight", "stable"))
    meta_insight = str(last_meta.get("insight", "balanced"))
    conflict_winner = str(last_conflict.get("winner", "balanced"))

    self_summary = f"I am currently driven by {conflict_winner}, with {dominant_trait} as my strongest trait."
    recent_change = f"My recent pattern is {reflection_insight}, and my meta-state is {meta_insight}."
    becoming = "I am becoming more exploratory." if conflict_winner == "explore" else (
        "I am becoming more persistent." if conflict_winner == "persist" else
        "I am becoming more stable."
    )

    narrative = {
        "timestamp": time.time(),
        "self_summary": self_summary,
        "recent_change": recent_change,
        "becoming": becoming,
        "dominant_trait": dominant_trait,
        "conflict_winner": conflict_winner,
        "reflection_insight": reflection_insight,
        "meta_insight": meta_insight
    }

    history = state.get("history", [])
    if not isinstance(history, list):
        history = []

    history.append(narrative)
    history = history[-MAX_HISTORY:]

    new_state = {
        "last_narrative": narrative,
        "history": history
    }

    _save(NARRATIVE_PATH, new_state)

    return {
        "status": "narrative_updated",
        "self_summary": self_summary,
        "recent_change": recent_change,
        "becoming": becoming,
        "history_length": len(history)
    }
