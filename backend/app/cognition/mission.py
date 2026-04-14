import json, os, time

MISSION_PATH = "backend/data/mission.json"
GOALS_PATH = "backend/data/goals.json"

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

def run(context=None):
    mission_data = _safe_load(MISSION_PATH, {"active_mission": None, "history": []})
    goals_data = _safe_load(GOALS_PATH, {"active_goals": []})

    active_goal = goals_data.get("active_goals", [])
    active_goal = active_goal[0] if active_goal else None

    active_mission = mission_data.get("active_mission")

    # 🔒 HARD LOCK: ALWAYS ensure mission exists if goal exists
    if active_goal:
        if not active_mission or active_mission.get("status") != "active":
            active_mission = {
                "id": f"mission_{int(time.time())}",
                "goal_type": active_goal.get("type"),
                "progress": active_goal.get("progress", 0.1),
                "status": "active",
                "created_at": time.time()
            }

            mission_data["active_mission"] = active_mission
            _safe_save(MISSION_PATH, mission_data)

            return {
                "status": "mission_hard_locked",
                "mission": active_mission
            }

    return {
        "status": "mission_stable",
        "active_mission": active_mission
    }
