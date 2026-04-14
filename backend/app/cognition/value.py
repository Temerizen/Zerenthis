import json
import os
import time
from typing import Dict, Any

DATA_PATH = "backend/data/value_system.json"

def _default() -> Dict[str, Any]:
    return {
        "preferences": {
            "exploration": 1.0,
            "efficiency": 1.0,
            "stability": 1.0,
            "novelty": 1.0
        },
        "history": [],
        "last_score": 0.0
    }

def _load() -> Dict[str, Any]:
    state = _default()
    if not os.path.exists(DATA_PATH):
        return state
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        if isinstance(loaded, dict):
            state.update(loaded)
    except Exception:
        return state

    if not isinstance(state.get("preferences"), dict):
        state["preferences"] = _default()["preferences"]
    if not isinstance(state.get("history"), list):
        state["history"] = []
    if not isinstance(state.get("last_score"), (int, float)):
        state["last_score"] = 0.0

    for k, v in _default()["preferences"].items():
        if not isinstance(state["preferences"].get(k), (int, float)):
            state["preferences"][k] = v

    return state

def _save(data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _extract_confidence(self_model: Dict[str, Any]) -> float:
    if not isinstance(self_model, dict):
        return 0.5

    direct = self_model.get("confidence")
    if isinstance(direct, (int, float)):
        return float(direct)

    identity = self_model.get("identity", {})
    if isinstance(identity, dict):
        nested = identity.get("confidence")
        if isinstance(nested, (int, float)):
            return float(nested)

    return 0.5

def _score(context: Dict[str, Any], prefs: Dict[str, float]) -> float:
    explore = context.get("explore", {})
    decision = context.get("decision", {})
    self_model = context.get("self_model", {})

    if not isinstance(explore, dict):
        explore = {}
    if not isinstance(decision, dict):
        decision = {}
    if not isinstance(self_model, dict):
        self_model = {}

    chosen = explore.get("chosen_strategy", "")
    novelty = 1.0 if chosen in ["test_new_action", "probe_unknown"] else 0.5
    efficiency = decision.get("confidence", 0.5)
    if not isinstance(efficiency, (int, float)):
        efficiency = 0.5

    stability = _extract_confidence(self_model)

    exploration = explore.get("exploration_drive", 0.5)
    if not isinstance(exploration, (int, float)):
        exploration = 0.5

    score = (
        novelty * prefs["novelty"] +
        efficiency * prefs["efficiency"] +
        stability * prefs["stability"] +
        exploration * prefs["exploration"]
    ) / 4.0

    return round(float(score), 4)

def _adjust_preferences(state: Dict[str, Any], score: float) -> None:
    prefs = state["preferences"]
    delta = score - float(state.get("last_score", 0.0))

    if delta > 0:
        prefs["exploration"] += 0.01
        prefs["novelty"] += 0.01
    else:
        prefs["stability"] += 0.01
        prefs["efficiency"] += 0.01

    for k in list(prefs.keys()):
        prefs[k] = max(0.1, min(2.0, float(prefs[k])))

    state["last_score"] = score

def run(context: Dict[str, Any]) -> Dict[str, Any]:
    state = _load()
    score = _score(context, state["preferences"])
    _adjust_preferences(state, score)

    state["history"].append({
        "t": time.time(),
        "score": score,
        "preferences": dict(state["preferences"])
    })
    state["history"] = state["history"][-200:]

    _save(state)

    return {
        "score": score,
        "preferences": state["preferences"],
        "history_size": len(state["history"])
    }
