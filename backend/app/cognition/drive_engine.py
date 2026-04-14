import json
import os
import time

DRIVE_PATH = "backend/data/drive_state.json"

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

def clamp(v):
    return max(0.0, min(1.0, v))

def run(context):
    state = _safe_load(DRIVE_PATH, {
        "curiosity": 0.5,
        "pressure": 0.5,
        "stability": 0.5,
        "last_update": None,
        "history": []
    })

    reflection = context.get("reflection", {})
    adaptive = context.get("adaptive", {})

    trend = reflection.get("trend")
    score = reflection.get("score", 0.5)
    adjustment = adaptive.get("adjustment")

    # =========================
    # DRIVE DYNAMICS
    # =========================

    # Pressure increases when declining
    if trend == "declining":
        state["pressure"] += 0.1
        state["stability"] -= 0.05

    # Stability increases when improving
    elif trend == "improving":
        state["stability"] += 0.1
        state["pressure"] -= 0.05

    # Curiosity increases when exploring
    if adjustment == "increase_exploration":
        state["curiosity"] += 0.1

    # Curiosity slightly decays when locked in
    elif adjustment == "reinforce_current_path":
        state["curiosity"] -= 0.03

    # General decay toward baseline
    state["curiosity"] += (0.5 - state["curiosity"]) * 0.05
    state["pressure"] += (0.5 - state["pressure"]) * 0.03
    state["stability"] += (0.5 - state["stability"]) * 0.03

    # Clamp values
    state["curiosity"] = clamp(state["curiosity"])
    state["pressure"] = clamp(state["pressure"])
    state["stability"] = clamp(state["stability"])

    snapshot = {
        "timestamp": time.time(),
        "curiosity": state["curiosity"],
        "pressure": state["pressure"],
        "stability": state["stability"],
        "trend": trend,
        "adjustment": adjustment,
        "score": score
    }

    state["last_update"] = snapshot
    state["history"].append(snapshot)

    if len(state["history"]) > 50:
        state["history"] = state["history"][-50:]

    _safe_save(DRIVE_PATH, state)

    return {
        "status": "drive_updated",
        "drives": {
            "curiosity": state["curiosity"],
            "pressure": state["pressure"],
            "stability": state["stability"]
        },
        "snapshot": snapshot
    }
