import json
import os
import time

IDENTITY_PATH = "backend/data/identity_stream.json"

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

def run(context):
    state = _safe_load(IDENTITY_PATH, {
        "current_focus": None,
        "last_goal_type": None,
        "last_mission_id": None,
        "continuity_score": 0.5,
        "cycle_count": 0,
        "narrative": [],
        "last_update": None
    })

    goal = context.get("goal")
    mission = context.get("mission")

    goal_type = goal.get("type") if isinstance(goal, dict) else None
    mission_id = mission.get("id") if isinstance(mission, dict) else None

    # Continuity logic
    same_goal = goal_type == state.get("last_goal_type")
    same_mission = mission_id == state.get("last_mission_id")

    if same_goal and same_mission:
        state["continuity_score"] = min(1.0, state["continuity_score"] + 0.05)
    else:
        state["continuity_score"] = max(0.0, state["continuity_score"] - 0.08)

    # Update identity
    state["current_focus"] = goal_type
    state["last_goal_type"] = goal_type
    state["last_mission_id"] = mission_id
    state["cycle_count"] += 1
    state["last_update"] = time.time()

    # Narrative entry
    entry = {
        "timestamp": time.time(),
        "goal": goal_type,
        "mission": mission_id,
        "continuity": state["continuity_score"]
    }

    state["narrative"].append(entry)

    # Keep narrative trimmed
    if len(state["narrative"]) > 50:
        state["narrative"] = state["narrative"][-50:]

    _safe_save(IDENTITY_PATH, state)

    return {
        "status": "identity_updated",
        "continuity_score": state["continuity_score"],
        "cycle_count": state["cycle_count"],
        "current_focus": state["current_focus"],
        "entry": entry
    }
