import json
import os
import time

RECOVERY_PATH = "backend/data/goal_recovery.json"
MEMORY_PATH = "backend/data/memory_depth.json"

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

def _goal_from_context(context):
    dominant_value = context.get("dominant_value") or "exploration"
    trend = context.get("trend") or "unstable"

    if dominant_value == "exploration":
        goal_type = "balanced_progression"
        description = "Recover and continue balanced progression"
    elif dominant_value == "persistence":
        goal_type = "mission_continuity"
        description = "Preserve mission continuity across instability"
    elif dominant_value == "stability":
        goal_type = "stabilize_system"
        description = "Stabilize internal direction and reduce drift"
    else:
        goal_type = "adaptive_progress"
        description = "Regain adaptive forward progress"

    if trend == "declining":
        description = f"{description} after performance decline"
    elif trend == "improving":
        description = f"{description} while preserving gains"

    return {
        "id": f"goal_recovered_{int(time.time())}",
        "type": goal_type,
        "description": description,
        "priority": 0.65,
        "commitment": 0.55,
        "progress": 0.0,
        "status": "active",
        "created_at": time.time(),
        "last_updated": time.time(),
        "cycles_active": 0,
        "source": "goal_recovery_engine"
    }

def run(context):
    recovery = _safe_load(RECOVERY_PATH, {
        "last_recovery": None,
        "history": []
    })

    active_goal = context.get("active_goal")
    if active_goal:
        return {
            "status": "goal_present",
            "recovered": False,
            "active_goal": active_goal
        }

    memory = _safe_load(MEMORY_PATH, {
        "recent_scores": [],
        "trend": "unstable",
        "last_pattern": None
    })

    recovered_goal = _goal_from_context({
        "dominant_value": context.get("dominant_value"),
        "trend": memory.get("trend", "unstable")
    })

    event = {
        "timestamp": time.time(),
        "reason": "goal_missing",
        "dominant_value": context.get("dominant_value"),
        "trend": memory.get("trend", "unstable"),
        "recovered_goal_id": recovered_goal["id"],
        "recovered_goal_type": recovered_goal["type"]
    }

    recovery["last_recovery"] = event
    recovery["history"].append(event)
    _safe_save(RECOVERY_PATH, recovery)

    return {
        "status": "goal_recovered",
        "recovered": True,
        "active_goal": recovered_goal,
        "recovery_event": event
    }
