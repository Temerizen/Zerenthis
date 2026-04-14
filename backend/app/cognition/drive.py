import json
import os
import time
from typing import Dict, Any

IDENTITY_PATH = "backend/data/identity_state.json"
REFLECTION_PATH = "backend/data/reflection_state.json"
CONFLICT_PATH = "backend/data/conflict_state.json"
DRIVE_PATH = "backend/data/drive_state.json"

DEFAULT_DRIVE_STATE = {
    "version": 1,
    "last_updated": None,
    "active_drive": "balance",
    "last_arbitration": None,
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


def _save(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _safe(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _choose_drive(traits: Dict[str, Any], conflict: Dict[str, Any], reflection: Dict[str, Any]) -> Dict[str, Any]:
    curiosity = _safe(traits.get("curiosity", 0.5), 0.5)
    stability = _safe(traits.get("stability_preference", 0.5), 0.5)
    persistence = _safe(traits.get("persistence", 0.5), 0.5)
    risk = _safe(traits.get("risk_tolerance", 0.5), 0.5)

    total_conflict = _safe(conflict.get("scores", {}).get("total_conflict", 0.0), 0.0)
    pattern = reflection.get("last_reflection", {}).get("pattern", "unknown")

    score_explore = curiosity + (risk * 0.35) - (stability * 0.15)
    score_stabilize = stability + (0.25 if total_conflict >= 0.3 else 0.0)
    score_persist = persistence + (0.15 if pattern == "stable_identity" else 0.0)
    score_balance = 0.6 - abs(curiosity - stability)

    candidates = {
        "explore": round(score_explore, 4),
        "stabilize": round(score_stabilize, 4),
        "persist": round(score_persist, 4),
        "balance": round(score_balance, 4)
    }

    active_drive = max(candidates, key=candidates.get)

    return {
        "active_drive": active_drive,
        "scores": candidates
    }


def run(context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    context = context or {}

    identity = _load(IDENTITY_PATH, {"traits": {}})
    reflection = _load(REFLECTION_PATH, {"last_reflection": {}})
    conflict = _load(CONFLICT_PATH, {"last_conflict": {"scores": {}}})
    drive_state = _load(DRIVE_PATH, DEFAULT_DRIVE_STATE)

    traits = identity.get("traits", {})
    if not isinstance(traits, dict):
        traits = {}

    arbitration = _choose_drive(
        traits=traits,
        conflict=conflict.get("last_conflict", {}) if isinstance(conflict.get("last_conflict", {}), dict) else {},
        reflection=reflection
    )

    entry = {
        "timestamp": time.time(),
        "active_drive": arbitration["active_drive"],
        "scores": arbitration["scores"],
        "dominant_trait": reflection.get("last_reflection", {}).get("dominant_trait", "unknown"),
        "conflict_label": conflict.get("last_conflict", {}).get("label", "unknown"),
        "pattern": reflection.get("last_reflection", {}).get("pattern", "unknown")
    }

    history = drive_state.get("history", [])
    if not isinstance(history, list):
        history = []

    history.append(entry)
    history = history[-MAX_HISTORY:]

    new_state = drive_state.copy()
    new_state["last_updated"] = time.time()
    new_state["active_drive"] = arbitration["active_drive"]
    new_state["last_arbitration"] = entry
    new_state["history"] = history

    _save(DRIVE_PATH, new_state)

    return {
        "status": "drive_arbitrated",
        "active_drive": arbitration["active_drive"],
        "scores": arbitration["scores"],
        "history_length": len(history)
    }
