import json, os, time

PRESSURE_PATH = "backend/data/pressure.json"
GOALS_PATH = "backend/data/goals.json"
MISSION_PATH = "backend/data/mission.json"

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

def _clamp(value, lo=0.0, hi=1.0):
    return max(lo, min(hi, value))

def _pressure_for(strategy, adjustment_action):
    goal_delta = 0.0
    mission_delta = 0.0
    mode = "neutral"

    if strategy == "optimize_focus":
        goal_delta += 0.04
        mission_delta += 0.05
        mode = "focused"

    elif strategy == "reduce_risk":
        goal_delta += 0.02
        mission_delta += 0.02
        mode = "stabilized"

    elif strategy == "explore_more":
        goal_delta += 0.01
        mission_delta += 0.04
        mode = "expansive"

    elif strategy == "increase_efficiency":
        goal_delta += 0.03
        mission_delta += 0.04
        mode = "efficient"

    else:
        goal_delta += 0.01
        mission_delta += 0.02
        mode = "default"

    if adjustment_action == "reinforce":
        goal_delta += 0.03
        mission_delta += 0.03
    elif adjustment_action == "destabilize":
        goal_delta -= 0.05
        mission_delta -= 0.03
        mode = "corrective"
    elif adjustment_action == "neutral_adjust":
        goal_delta += 0.0
        mission_delta += 0.0

    return {
        "goal_delta": goal_delta,
        "mission_delta": mission_delta,
        "mode": mode
    }

def run(context):
    pressure_data = _safe_load(PRESSURE_PATH, {"last_pressure": None, "history": []})
    goals_data = _safe_load(GOALS_PATH, {"active_goals": [], "history": []})
    mission_data = _safe_load(MISSION_PATH, {"active_mission": None, "history": []})

    strategy = context.get("strategy", "default")
    adjustment_action = context.get("adjustment_action", "neutral_adjust")

    active_goals = goals_data.get("active_goals", [])
    active_goal = active_goals[0] if active_goals else None
    active_mission = mission_data.get("active_mission")

    pressure = _pressure_for(strategy, adjustment_action)

    changed_goal = False
    changed_mission = False

    if active_goal:
        active_goal["commitment"] = _clamp(active_goal.get("commitment", 0.5) + pressure["goal_delta"])
        active_goal["last_updated"] = time.time()
        changed_goal = True
        goals_data["active_goals"] = [active_goal]
        _safe_save(GOALS_PATH, goals_data)

    if active_mission:
        active_mission["progress"] = _clamp(active_mission.get("progress", 0.0) + pressure["mission_delta"])
        active_mission["last_updated"] = time.time()
        changed_mission = True

        if active_mission["progress"] >= 1.0:
            active_mission["status"] = "completed"
            mission_data.setdefault("history", []).append(active_mission)
            mission_data["active_mission"] = None
        else:
            mission_data["active_mission"] = active_mission

        _safe_save(MISSION_PATH, mission_data)

    pressure_record = {
        "timestamp": time.time(),
        "strategy": strategy,
        "adjustment_action": adjustment_action,
        "mode": pressure["mode"],
        "goal_delta": pressure["goal_delta"],
        "mission_delta": pressure["mission_delta"],
        "changed_goal": changed_goal,
        "changed_mission": changed_mission
    }

    pressure_data["last_pressure"] = pressure_record
    pressure_data["history"].append(pressure_record)

    if len(pressure_data["history"]) > 50:
        pressure_data["history"] = pressure_data["history"][-50:]

    _safe_save(PRESSURE_PATH, pressure_data)

    updated_mission_data = _safe_load(MISSION_PATH, {"active_mission": None, "history": []})

    return {
        "status": "pressure_applied",
        "pressure": pressure_record,
        "goal_commitment": active_goal.get("commitment") if active_goal else None,
        "mission_progress": updated_mission_data.get("active_mission", {}).get("progress") if updated_mission_data.get("active_mission") else None
    }
