import json, os, time, random

INIT_PATH = "backend/data/initiative.json"
AUTO_PATH = "backend/data/autonomous_mission.json"
REALITY_PATH = "backend/data/reality.json"
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

def _clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))

def run():
    data = _safe_load(INIT_PATH, {"last_action": None, "history": []})
    auto = _safe_load(AUTO_PATH, {"active_directive": None})
    reality = _safe_load(REALITY_PATH, {"last_outcome": None})
    mission = _safe_load(MISSION_PATH, {"active_mission": None})

    directive = auto.get("active_directive")
    last_outcome = reality.get("last_outcome")
    active_mission = mission.get("active_mission")

    if not directive or not active_mission:
        return {"status": "no_initiative", "reason": "missing_context"}

    protection = float(directive.get("protection", 0.0))
    priority = float(directive.get("priority", 0.0))
    score = float(last_outcome.get("score", 0.5)) if last_outcome else 0.5

    # 🧠 initiative drive calculation
    drive = (
        (protection * 0.4) +
        (priority * 0.3) +
        (score * 0.3)
    )

    drive = _clamp(drive)

    action = "idle"

    if drive > 0.75:
        # strong initiative → push mission forward
        action = "advance_mission"
        active_mission["progress"] = _clamp(active_mission.get("progress", 0.0) + 0.03)

    elif drive > 0.55:
        # moderate → reinforce
        action = "reinforce_focus"

    else:
        # weak → observe
        action = "observe"

    record = {
        "timestamp": time.time(),
        "drive": round(drive, 4),
        "action": action,
        "mission_id": active_mission.get("id")
    }

    data["last_action"] = record
    data["history"].append(record)
    data["history"] = data["history"][-50:]

    _safe_save(INIT_PATH, data)

    # save mission if modified
    if action == "advance_mission":
        _safe_save(MISSION_PATH, mission)

    return {
        "status": "initiative_evaluated",
        "drive": drive,
        "action": action,
        "mission_progress": active_mission.get("progress")
    }
