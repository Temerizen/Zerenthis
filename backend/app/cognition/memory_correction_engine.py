import json
import os
import time

GOALS_PATH = "backend/data/goals.json"
CORRECTION_PATH = "backend/data/memory_correction.json"

VALID_GOAL_TYPES = {
    "balanced_progression",
    "exploration",
    "optimization",
    "stabilization",
    "mission_continuity",
    "adaptive_progress"
}

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

def _goal_invalid(goal):
    if not isinstance(goal, dict):
        return True
    goal_type = goal.get("type")
    return (not goal_type) or (goal_type == "unknown") or (goal_type not in VALID_GOAL_TYPES)

def run(context):
    correction_log = _safe_load(CORRECTION_PATH, {
        "last_correction": None,
        "history": []
    })

    goals_state = _safe_load(GOALS_PATH, {
        "active_goals": [],
        "history": []
    })

    aligned_goal = context.get("aligned_goal")
    active_goals = goals_state.get("active_goals", [])

    if not aligned_goal:
        return {
            "status": "no_aligned_goal",
            "corrected": False
        }

    corrected = False
    reason = "already_clean"

    if not active_goals:
        goals_state["active_goals"] = [aligned_goal]
        corrected = True
        reason = "missing_active_goal_replaced"

    else:
        first_goal = active_goals[0]
        if _goal_invalid(first_goal):
            goals_state["history"].append(first_goal)
            goals_state["active_goals"] = [aligned_goal]
            corrected = True
            reason = "invalid_goal_rewritten"
        elif first_goal.get("type") != aligned_goal.get("type"):
            goals_state["history"].append(first_goal)
            goals_state["active_goals"] = [aligned_goal]
            corrected = True
            reason = "mismatched_goal_rebound"

    if corrected:
        _safe_save(GOALS_PATH, goals_state)

    event = {
        "timestamp": time.time(),
        "corrected": corrected,
        "reason": reason,
        "aligned_goal_type": aligned_goal.get("type"),
        "stored_goal_type": goals_state.get("active_goals", [{}])[0].get("type") if goals_state.get("active_goals") else None
    }

    correction_log["last_correction"] = event
    correction_log["history"].append(event)
    _safe_save(CORRECTION_PATH, correction_log)

    return {
        "status": "memory_correction_evaluated",
        "corrected": corrected,
        "reason": reason,
        "event": event
    }
