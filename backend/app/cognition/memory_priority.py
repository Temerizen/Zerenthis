import json
import os
import time
from typing import Dict, Any, List

DATA_PATH = "backend/data/memory_priority.json"

def _default() -> Dict[str, Any]:
    return {
        "memories": [],
        "stats": {
            "total_memories": 0,
            "high_value_memories": 0
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
        if not isinstance(base.get("memories"), list):
            base["memories"] = []
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

def _compute_importance(context: Dict[str, Any]) -> float:
    decision = context.get("decision", {}) or {}
    value = context.get("value", {}) or {}
    execution = context.get("execution", {}) or {}
    intent = context.get("intent", {}) or {}
    explore = context.get("explore", {}) or {}

    decision_conf = _safe_float(decision.get("confidence"), 0.5)
    value_score = _safe_float(value.get("score"), 0.5)
    explore_success = 1.0 if explore.get("success") else 0.0

    current_intent = intent.get("current_intent", "balanced_progression")
    goal = execution.get("goal", "balanced_progression")
    intent_match = 1.0 if current_intent == goal else 0.4

    raw = (
        decision_conf * 0.35 +
        value_score * 0.30 +
        explore_success * 0.15 +
        intent_match * 0.20
    )

    return round(max(0.0, min(1.0, raw)), 4)

def _build_memory(context: Dict[str, Any], importance: float) -> Dict[str, Any]:
    decision = context.get("decision", {}) or {}
    goal = context.get("goal", {}) or {}
    intent = context.get("intent", {}) or {}
    execution = context.get("execution", {}) or {}
    explore = context.get("explore", {}) or {}

    return {
        "t": time.time(),
        "importance": importance,
        "decision": decision.get("legacy_chosen_action_DISABLED"),
        "goal": goal.get("active_goal"),
        "intent": intent.get("current_intent"),
        "execution_goal": execution.get("goal"),
        "execution_detail": (execution.get("execution") or {}).get("detail"),
        "strategy": explore.get("chosen_strategy"),
        "success": explore.get("success", False)
    }

def _decay_and_sort(memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for m in memories:
        importance = _safe_float(m.get("importance"), 0.5)
        age_penalty = 0.995
        m["importance"] = round(max(0.05, importance * age_penalty), 4)

    memories.sort(key=lambda x: _safe_float(x.get("importance"), 0.0), reverse=True)
    return memories[:200]

def run(context: Dict[str, Any]) -> Dict[str, Any]:
    state = _load()

    importance = _compute_importance(context)
    memory = _build_memory(context, importance)

    state["memories"].append(memory)
    state["memories"] = _decay_and_sort(state["memories"])

    state["stats"]["total_memories"] = len(state["memories"])
    state["stats"]["high_value_memories"] = len(
        [m for m in state["memories"] if _safe_float(m.get("importance"), 0.0) >= 0.75]
    )

    _save(state)

    top = state["memories"][0] if state["memories"] else memory

    return {
        "status": "memory_updated",
        "stored_importance": importance,
        "top_memory": top,
        "stats": state["stats"]
    }
