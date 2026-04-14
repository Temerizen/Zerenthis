import json
import os
import time
from typing import Dict, Any, List

DATA_PATH = "backend/data/goal_generation.json"

def _default() -> Dict[str, Any]:
    return {
        "history": [],
        "last_selected": None,
        "stats": {
            "total_cycles": 0
        }
    }

def _load() -> Dict[str, Any]:
    if not os.path.exists(DATA_PATH):
        return _default()
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        base = _default()
        if isinstance(data, dict):
            base.update(data)
        if not isinstance(base.get("history"), list):
            base["history"] = []
        if not isinstance(base.get("stats"), dict):
            base["stats"] = _default()["stats"]
        return base
    except Exception:
        return _default()

def _save(data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _safe_float(value: Any, fallback: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return fallback

def _generate_candidates(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    explore = context.get("explore", {}) or {}
    value = context.get("value", {}) or {}
    intent = context.get("intent", {}) or {}
    self_model = context.get("self_model", {}) or {}

    explore_strategy = explore.get("chosen_strategy", "repeat_successful")
    value_score = _safe_float(value.get("score"), 0.5)
    current_intent = intent.get("current_intent", "balanced_progression")
    confidence = _safe_float(self_model.get("confidence"), 0.5)

    candidates = [
        {
            "goal": "expand_capabilities",
            "reason": "exploration momentum",
            "score": 0.0
        },
        {
            "goal": "analyze_environment",
            "reason": "world awareness",
            "score": 0.0
        },
        {
            "goal": "optimize_strategy",
            "reason": "improve internal methods",
            "score": 0.0
        },
        {
            "goal": "improve_stability",
            "reason": "increase consistency",
            "score": 0.0
        },
        {
            "goal": "balanced_progression",
            "reason": "general advancement",
            "score": 0.0
        }
    ]

    for c in candidates:
        score = 0.2

        if c["goal"] == "expand_capabilities":
            if explore_strategy in ["test_new_action", "probe_unknown", "modify_known", "stress_test"]:
                score += 0.35
            if current_intent == "expand_capabilities":
                score += 0.2
            score += value_score * 0.25

        elif c["goal"] == "analyze_environment":
            score += 0.15
            score += value_score * 0.15

        elif c["goal"] == "optimize_strategy":
            if confidence >= 0.6:
                score += 0.2
            score += value_score * 0.2

        elif c["goal"] == "improve_stability":
            if confidence < 0.65:
                score += 0.35
            score += (1.0 - confidence) * 0.2

        elif c["goal"] == "balanced_progression":
            score += 0.2
            score += value_score * 0.1

        c["score"] = round(min(1.0, score), 4)

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates

def run(context: Dict[str, Any]) -> Dict[str, Any]:
    state = _load()

    candidates = _generate_candidates(context)
    selected = candidates[0]

    state["last_selected"] = selected["goal"]
    state["stats"]["total_cycles"] = int(state["stats"].get("total_cycles", 0)) + 1
    state["history"].append({
        "t": time.time(),
        "selected": selected,
        "candidates": candidates
    })
    state["history"] = state["history"][-200:]

    _save(state)

    return {
        "status": "goal_generated",
        "selected_goal": selected["goal"],
        "reason": selected["reason"],
        "candidates": candidates,
        "stats": state["stats"]
    }
