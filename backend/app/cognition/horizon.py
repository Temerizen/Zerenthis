import json
import os
import time
from typing import Dict, Any

DATA_PATH = "backend/data/horizon_planning.json"

def _default():
    return {
        "history": [],
        "last_plan": None
    }

def _load():
    if not os.path.exists(DATA_PATH):
        return _default()
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        base = _default()
        if isinstance(data, dict):
            base.update(data)
        return base
    except:
        return _default()

def _save(data):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def run(context: Dict[str, Any]) -> Dict[str, Any]:
    state = _load()

    goal = context.get("goal", "balanced_progression")
    intent = context.get("intent", {}).get("current_intent", goal)

    # Immediate (next step)
    immediate = [
        f"analyze_{goal}",
        f"execute_{goal}"
    ]

    # Short-term (next few cycles)
    short_term = [
        f"refine_{goal}",
        f"optimize_{goal}",
        f"stabilize_{goal}"
    ]

    # Long-term direction
    long_term = {
        "trajectory": intent,
        "objective": f"maximize_{intent}",
        "mode": "adaptive_growth"
    }

    plan = {
        "t": time.time(),
        "goal": goal,
        "intent": intent,
        "immediate": immediate,
        "short_term": short_term,
        "long_term": long_term
    }

    state["last_plan"] = plan
    state["history"].append(plan)
    state["history"] = state["history"][-100:]

    _save(state)

    return {
        "status": "multi_horizon_plan_created",
        "goal": goal,
        "intent": intent,
        "immediate": immediate,
        "short_term": short_term,
        "long_term": long_term
    }
