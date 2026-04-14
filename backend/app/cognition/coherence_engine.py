import json, os, time

GOALS_PATH = "backend/data/goals.json"
MISSION_PATH = "backend/data/mission.json"
COHERENCE_PATH = "backend/data/coherence.json"

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

def _create_goal_from_mission(mission):
    return {
        "id": f"goal_reconstructed_{int(time.time())}",
        "type": mission.get("goal_type", "reconstructed"),
        "description": f"Reconstructed from mission: {mission.get('description')}",
        "priority": 0.5,
        "commitment": 0.5,
        "progress": mission.get("progress", 0.0),
        "status": "active",
        "created_at": time.time(),
        "last_updated": time.time(),
        "cycles_active": 0,
        "source": "reconstructed_from_mission"
    }

def run():
    goals_data = _safe_load(GOALS_PATH, {"active_goals": [], "history": []})
    mission_data = _safe_load(MISSION_PATH, {"active_mission": None, "history": []})
    coherence_data = _safe_load(COHERENCE_PATH, {"last_check": None, "history": []})

    active_goals = goals_data.get("active_goals", [])
    active_goal = active_goals[0] if active_goals else None
    active_mission = mission_data.get("active_mission")

    action = "aligned"

    # CASE 1: Mission exists but no goal → reconstruct goal
    if active_mission and not active_goal:
        new_goal = _create_goal_from_mission(active_mission)
        goals_data["active_goals"] = [new_goal]
        _safe_save(GOALS_PATH, goals_data)
        action = "goal_reconstructed_from_mission"
        active_goal = new_goal

    # CASE 2: Goal exists but no mission → allow system to create later
    elif active_goal and not active_mission:
        action = "waiting_for_mission"

    # CASE 3: Both exist → validate alignment
    elif active_goal and active_mission:
        if active_goal.get("type") != active_mission.get("goal_type"):
            action = "mismatch_detected"

    record = {
        "timestamp": time.time(),
        "action": action,
        "has_goal": active_goal is not None,
        "has_mission": active_mission is not None
    }

    coherence_data["last_check"] = record
    coherence_data["history"].append(record)
    coherence_data["history"] = coherence_data["history"][-50:]

    _safe_save(COHERENCE_PATH, coherence_data)

    return {
        "status": "coherence_checked",
        "action": action,
        "active_goal": active_goal,
        "active_mission": active_mission
    }
