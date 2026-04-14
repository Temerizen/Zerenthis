import json, os, time

GOALS_PATH = "backend/data/goals.json"
MISSION_PATH = "backend/data/mission.json"
CORRECTION_PATH = "backend/data/self_correction.json"

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

def _build_goal_from_mission(mission, prior_goal=None):
    prior_goal = prior_goal or {}
    now = time.time()
    return {
        "id": prior_goal.get("id", f"goal_corrected_{int(now)}"),
        "type": mission.get("goal_type", "corrected"),
        "description": f"Aligned to mission: {mission.get('description', 'unknown mission')}",
        "priority": prior_goal.get("priority", 0.6),
        "commitment": max(prior_goal.get("commitment", 0.5), 0.55),
        "progress": max(prior_goal.get("progress", 0.0), mission.get("progress", 0.0)),
        "status": "active",
        "created_at": prior_goal.get("created_at", now),
        "last_updated": now,
        "cycles_active": prior_goal.get("cycles_active", 0),
        "source": "self_corrected_from_mission"
    }

def run():
    goals_data = _safe_load(GOALS_PATH, {"active_goals": [], "history": []})
    mission_data = _safe_load(MISSION_PATH, {"active_mission": None, "history": []})
    correction_data = _safe_load(CORRECTION_PATH, {"last_correction": None, "history": []})

    active_goals = goals_data.get("active_goals", [])
    active_goal = active_goals[0] if active_goals else None
    active_mission = mission_data.get("active_mission")

    action = "no_change"
    corrected_goal = active_goal

    if active_goal and active_mission:
        goal_type = active_goal.get("type")
        mission_goal_type = active_mission.get("goal_type")

        if goal_type != mission_goal_type:
            corrected_goal = _build_goal_from_mission(active_mission, active_goal)
            goals_data["active_goals"] = [corrected_goal]
            _safe_save(GOALS_PATH, goals_data)
            action = "goal_aligned_to_mission"

    record = {
        "timestamp": time.time(),
        "action": action,
        "goal_type_before": active_goal.get("type") if active_goal else None,
        "goal_type_after": corrected_goal.get("type") if corrected_goal else None,
        "mission_goal_type": active_mission.get("goal_type") if active_mission else None,
        "has_goal": corrected_goal is not None,
        "has_mission": active_mission is not None
    }

    correction_data["last_correction"] = record
    correction_data["history"].append(record)
    correction_data["history"] = correction_data["history"][-50:]
    _safe_save(CORRECTION_PATH, correction_data)

    return {
        "status": "self_correction_checked",
        "action": action,
        "active_goal": corrected_goal,
        "active_mission": active_mission,
        "record": record
    }
