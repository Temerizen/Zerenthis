import json, os, time

STATUS_PATH = "backend/data/status.json"
GOALS_PATH = "backend/data/goals.json"
MISSION_PATH = "backend/data/mission.json"
REALITY_PATH = "backend/data/reality.json"
ADAPT_PATH = "backend/data/adaptation.json"
STRATEGY_PATH = "backend/data/strategy.json"
PRESSURE_PATH = "backend/data/pressure.json"
EVOLUTION_PATH = "backend/data/strategy_evolution.json"
COHERENCE_PATH = "backend/data/coherence.json"
CORRECTION_PATH = "backend/data/self_correction.json"
AUTO_MISSION_PATH = "backend/data/autonomous_mission.json"

def _safe_load(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def _save(data):
    with open(STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def run():
    status_data = _safe_load(STATUS_PATH, {"last_snapshot": None, "history": []})
    goals = _safe_load(GOALS_PATH, {"active_goals": [], "history": []})
    mission = _safe_load(MISSION_PATH, {"active_mission": None, "history": []})
    reality = _safe_load(REALITY_PATH, {"history": [], "last_outcome": None})
    adaptation = _safe_load(ADAPT_PATH, {"last_adjustment": None, "history": []})
    strategy = _safe_load(STRATEGY_PATH, {"current_strategy": "default", "history": []})
    pressure = _safe_load(PRESSURE_PATH, {"last_pressure": None, "history": []})
    evolution = _safe_load(EVOLUTION_PATH, {"current_profile": None, "history": []})
    coherence = _safe_load(COHERENCE_PATH, {"last_check": None, "history": []})
    correction = _safe_load(CORRECTION_PATH, {"last_correction": None, "history": []})
    autonomous = _safe_load(AUTO_MISSION_PATH, {"active_directive": None, "history": []})

    active_goal = goals.get("active_goals", [])
    active_goal = active_goal[0] if active_goal else None

    active_mission = mission.get("active_mission")
    last_outcome = reality.get("last_outcome")
    last_adjustment = adaptation.get("last_adjustment")
    current_strategy = strategy.get("current_strategy", "default")
    last_pressure = pressure.get("last_pressure")
    current_profile = evolution.get("current_profile")
    last_coherence = coherence.get("last_check")
    last_correction = correction.get("last_correction")
    active_directive = autonomous.get("active_directive")

    snapshot = {
        "timestamp": time.time(),
        "goal": active_goal,
        "mission": active_mission,
        "last_outcome": last_outcome,
        "last_adjustment": last_adjustment,
        "current_strategy": current_strategy,
        "last_pressure": last_pressure,
        "strategy_profile": current_profile,
        "last_coherence": last_coherence,
        "last_correction": last_correction,
        "active_directive": active_directive,
        "summary": {
            "has_goal": active_goal is not None,
            "has_mission": active_mission is not None,
            "goal_type": active_goal.get("type") if active_goal else None,
            "mission_goal_type": active_mission.get("goal_type") if active_mission else None,
            "goal_commitment": active_goal.get("commitment") if active_goal else None,
            "goal_progress": active_goal.get("progress") if active_goal else None,
            "mission_progress": active_mission.get("progress") if active_mission else None,
            "last_score": last_outcome.get("score") if last_outcome else None,
            "last_adjustment_action": last_adjustment.get("action") if last_adjustment else None,
            "strategy": current_strategy,
            "pressure_mode": last_pressure.get("mode") if last_pressure else None,
            "strategy_tendency": current_profile.get("tendency") if current_profile else None,
            "strategy_stage": current_profile.get("evolution_stage") if current_profile else None,
            "coherence_action": last_coherence.get("action") if last_coherence else None,
            "correction_action": last_correction.get("action") if last_correction else None,
            "directive_priority": active_directive.get("priority") if active_directive else None,
            "directive_protection": active_directive.get("protection") if active_directive else None,
            "directive_action": active_directive.get("status") if active_directive else None
        }
    }

    status_data["last_snapshot"] = snapshot
    status_data["history"].append(snapshot)
    status_data["history"] = status_data["history"][-25:]

    _save(status_data)

    return {
        "status": "snapshot_created",
        "snapshot": snapshot
    }
