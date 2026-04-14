import json, os, time

AUTO_MISSION_PATH = "backend/data/autonomous_mission.json"
GOALS_PATH = "backend/data/goals.json"
MISSION_PATH = "backend/data/mission.json"
REALITY_PATH = "backend/data/reality.json"
ADAPT_PATH = "backend/data/adaptation.json"

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

def _build_directive(goal, mission, last_score, last_adjustment):
    protection = 0.5
    priority = 0.5

    if goal:
        priority += min(goal.get("commitment", 0.0), 0.3)
        priority += min(goal.get("progress", 0.0) * 0.2, 0.2)

    if mission:
        protection += min(mission.get("progress", 0.0) * 0.3, 0.3)

    if isinstance(last_score, (int, float)):
        if last_score >= 0.7:
            protection += 0.15
            priority += 0.1
        elif last_score < 0.4:
            protection -= 0.15
            priority -= 0.1

    if last_adjustment == "reinforce":
        protection += 0.1
    elif last_adjustment == "destabilize":
        protection -= 0.15

    protection = _clamp(protection)
    priority = _clamp(priority)

    return {
        "id": f"directive_{int(time.time())}",
        "goal_type": goal.get("type") if goal else None,
        "mission_id": mission.get("id") if mission else None,
        "mission_goal_type": mission.get("goal_type") if mission else None,
        "priority": priority,
        "protection": protection,
        "status": "active",
        "switch_resistance": protection,
        "created_at": time.time(),
        "last_updated": time.time(),
        "reason": "autonomous_mission_selection"
    }

def run():
    auto_data = _safe_load(AUTO_MISSION_PATH, {"active_directive": None, "history": []})
    goals_data = _safe_load(GOALS_PATH, {"active_goals": [], "history": []})
    mission_data = _safe_load(MISSION_PATH, {"active_mission": None, "history": []})
    reality_data = _safe_load(REALITY_PATH, {"history": [], "last_outcome": None})
    adapt_data = _safe_load(ADAPT_PATH, {"last_adjustment": None, "history": []})

    active_goals = goals_data.get("active_goals", [])
    active_goal = active_goals[0] if active_goals else None
    active_mission = mission_data.get("active_mission")
    last_outcome = reality_data.get("last_outcome")
    last_adjustment = adapt_data.get("last_adjustment")

    last_score = last_outcome.get("score") if last_outcome else None
    adjustment_action = last_adjustment.get("action") if last_adjustment else None

    existing = auto_data.get("active_directive")
    action = "no_directive"

    if active_goal and active_mission:
        if not existing:
            existing = _build_directive(active_goal, active_mission, last_score, adjustment_action)
            auto_data["active_directive"] = existing
            action = "directive_created"
        else:
            same_mission = existing.get("mission_id") == active_mission.get("id")
            same_goal = existing.get("goal_type") == active_goal.get("type")

            if same_mission and same_goal:
                protection = existing.get("protection", 0.5)
                priority = existing.get("priority", 0.5)

                if isinstance(last_score, (int, float)):
                    if last_score >= 0.7:
                        protection += 0.05
                        priority += 0.03
                    elif last_score < 0.4:
                        protection -= 0.08
                        priority -= 0.05

                if adjustment_action == "reinforce":
                    protection += 0.04
                elif adjustment_action == "destabilize":
                    protection -= 0.08

                existing["protection"] = _clamp(protection)
                existing["priority"] = _clamp(priority)
                existing["switch_resistance"] = existing["protection"]
                existing["last_updated"] = time.time()
                action = "directive_reinforced"
            else:
                current_resistance = existing.get("switch_resistance", 0.5)
                challenger_strength = 0.5
                if active_goal:
                    challenger_strength += min(active_goal.get("commitment", 0.0) * 0.3, 0.3)
                if isinstance(last_score, (int, float)) and last_score < 0.4:
                    challenger_strength += 0.15

                if challenger_strength > current_resistance:
                    auto_data.setdefault("history", []).append(existing)
                    existing = _build_directive(active_goal, active_mission, last_score, adjustment_action)
                    auto_data["active_directive"] = existing
                    action = "directive_switched"
                else:
                    action = "directive_protected"

    elif existing and (not active_goal or not active_mission):
        existing["status"] = "degraded"
        existing["last_updated"] = time.time()
        auto_data["active_directive"] = existing
        action = "directive_degraded"

    auto_data["history"] = auto_data.get("history", [])[-50:]
    _safe_save(AUTO_MISSION_PATH, auto_data)

    return {
        "status": "autonomous_mission_evaluated",
        "action": action,
        "active_directive": auto_data.get("active_directive")
    }
