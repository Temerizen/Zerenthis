import json
import os
import time

ALIGN_PATH = "backend/data/goal_alignment.json"

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

def _canonical_goal_from_mission(active_mission):
    goal_type = active_mission.get("goal_type") or "balanced_progression"
    return {
        "id": f"goal_aligned_{int(time.time())}",
        "type": goal_type,
        "description": f"Aligned to mission: {goal_type}",
        "priority": 0.7,
        "commitment": 0.6,
        "progress": 0.0,
        "status": "active",
        "created_at": time.time(),
        "last_updated": time.time(),
        "cycles_active": 0,
        "source": "goal_alignment_engine"
    }

def _canonical_goal_from_value(dominant_value):
    mapping = {
        "exploration": ("balanced_progression", "Recover balanced progression from exploratory pressure"),
        "persistence": ("mission_continuity", "Restore mission continuity"),
        "stability": ("stabilization", "Stabilize internal direction"),
        "efficiency": ("optimization", "Optimize execution path"),
    }
    goal_type, description = mapping.get(
        dominant_value,
        ("adaptive_progress", "Recover adaptive progress")
    )
    return {
        "id": f"goal_aligned_{int(time.time())}",
        "type": goal_type,
        "description": description,
        "priority": 0.68,
        "commitment": 0.58,
        "progress": 0.0,
        "status": "active",
        "created_at": time.time(),
        "last_updated": time.time(),
        "cycles_active": 0,
        "source": "goal_alignment_engine"
    }

def run(context):
    state = _safe_load(ALIGN_PATH, {
        "last_alignment": None,
        "history": []
    })

    active_goal = context.get("active_goal")
    active_mission = context.get("active_mission")
    dominant_value = context.get("dominant_value")

    goal_type = None
    if isinstance(active_goal, dict):
        goal_type = active_goal.get("type")

    aligned_goal = active_goal
    action = "kept"
    reason = "already_valid"

    invalid_goal = (
        active_goal is None or
        not isinstance(active_goal, dict) or
        not goal_type or
        goal_type == "unknown" or
        goal_type not in VALID_GOAL_TYPES
    )

    mission_goal_type = None
    if isinstance(active_mission, dict):
        mission_goal_type = active_mission.get("goal_type")

    if invalid_goal and active_mission:
        aligned_goal = _canonical_goal_from_mission(active_mission)
        action = "realigned_from_mission"
        reason = "invalid_or_unknown_goal"

    elif invalid_goal:
        aligned_goal = _canonical_goal_from_value(dominant_value)
        action = "reconstructed_from_value"
        reason = "invalid_or_missing_goal"

    elif active_mission and mission_goal_type and goal_type != mission_goal_type:
        aligned_goal = _canonical_goal_from_mission(active_mission)
        action = "rebound_to_mission"
        reason = "goal_mission_mismatch"

    event = {
        "timestamp": time.time(),
        "action": action,
        "reason": reason,
        "goal_type_before": goal_type,
        "mission_goal_type": mission_goal_type,
        "goal_type_after": aligned_goal.get("type") if isinstance(aligned_goal, dict) else None
    }

    state["last_alignment"] = event
    state["history"].append(event)
    _safe_save(ALIGN_PATH, state)

    return {
        "status": "alignment_evaluated",
        "action": action,
        "reason": reason,
        "aligned_goal": aligned_goal,
        "event": event
    }
