import json
import os
import time

ADAPT_PATH = "backend/data/adaptive_intent.json"

def _safe_load(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def _safe_save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def run(context):
    state = _safe_load(ADAPT_PATH, {
        "last_adjustment": None,
        "history": []
    })

    reflection = context.get("reflection", {})
    goal = context.get("goal", {})

    trend = reflection.get("trend")
    decision = reflection.get("decision")

    adjustment = "none"
    intensity = 0.0

    # =========================
    # ADAPTIVE LOGIC
    # =========================
    if trend == "declining":
        adjustment = "increase_exploration"
        intensity = 0.7

    elif trend == "improving":
        adjustment = "reinforce_current_path"
        intensity = 0.8

    elif decision == "reconsider":
        adjustment = "shift_strategy"
        intensity = 0.9

    elif decision == "continue":
        adjustment = "lock_in"
        intensity = 1.0

    else:
        adjustment = "observe"
        intensity = 0.3

    result = {
        "timestamp": time.time(),
        "adjustment": adjustment,
        "intensity": intensity,
        "trend": trend,
        "decision": decision,
        "goal": goal.get("type")
    }

    state["last_adjustment"] = result
    state["history"].append(result)

    if len(state["history"]) > 50:
        state["history"] = state["history"][-50:]

    _safe_save(ADAPT_PATH, state)

    return {
        "status": "adaptive_intent_applied",
        "adjustment": result
    }
