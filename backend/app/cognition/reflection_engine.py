import json
import os
import time

REFLECTION_PATH = "backend/data/reflection_state.json"

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

def _evaluate(score):
    if score >= 0.75:
        return "positive"
    elif score <= 0.45:
        return "negative"
    return "neutral"

def run(context):
    state = _safe_load(REFLECTION_PATH, {
        "last_reflection": None,
        "history": []
    })

    score = context.get("score", 0.5)
    goal_type = context.get("goal_type")
    continuity = context.get("continuity", 0.5)

    evaluation = _evaluate(score)

    # =========================
    # SAFE PREVIOUS STATE
    # =========================
    prev = state.get("last_reflection")
    prev = prev if isinstance(prev, dict) else {}

    prev_score = prev.get("score")

    if prev_score is not None:
        if score > prev_score:
            trend = "improving"
        elif score < prev_score:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "unknown"

    # =========================
    # DECISION LOGIC
    # =========================
    if evaluation == "positive" and continuity > 0.5:
        decision = "continue"
        note = "Stable and effective behavior"
    elif evaluation == "negative":
        decision = "reconsider"
        note = "Performance drop detected"
    else:
        decision = "observe"
        note = "Monitoring behavior"

    reflection = {
        "timestamp": time.time(),
        "score": score,
        "evaluation": evaluation,
        "trend": trend,
        "goal": goal_type,
        "continuity": continuity,
        "decision": decision,
        "note": note
    }

    state["last_reflection"] = reflection
    state["history"].append(reflection)

    if len(state["history"]) > 50:
        state["history"] = state["history"][-50:]

    _safe_save(REFLECTION_PATH, state)

    return {
        "status": "reflection_generated",
        "reflection": reflection
    }
