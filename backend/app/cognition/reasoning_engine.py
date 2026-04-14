import json, os, time

REASON_PATH = "backend/data/reasoning.json"
INIT_PATH = "backend/data/initiative.json"
REALITY_PATH = "backend/data/reality.json"
AUTO_PATH = "backend/data/autonomous_mission.json"

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

def run():
    data = _safe_load(REASON_PATH, {"last_reasoning": None, "history": []})
    initiative = _safe_load(INIT_PATH, {"last_action": None})
    reality = _safe_load(REALITY_PATH, {"last_outcome": None})
    auto = _safe_load(AUTO_PATH, {"active_directive": None})

    last_action = initiative.get("last_action")
    last_outcome = reality.get("last_outcome")
    directive = auto.get("active_directive")

    if not last_action:
        return {"status": "no_reasoning", "reason": "no_action"}

    score = float(last_outcome.get("score", 0.5)) if last_outcome else 0.5
    protection = float(directive.get("protection", 0.0)) if directive else 0.0

    # 🧠 explain why action happened
    if last_action["action"] == "advance_mission":
        reason = "high_drive_due_to_alignment"
    elif last_action["action"] == "reinforce_focus":
        reason = "moderate_confidence"
    else:
        reason = "low_drive_observation_mode"

    # 🔮 simulate alternative
    if score > 0.75:
        alternative = "continue_current_path"
        alt_score_estimate = score - 0.05
    else:
        alternative = "change_strategy"
        alt_score_estimate = score + 0.1

    # ⚖️ decision comparison
    chosen_better = score >= alt_score_estimate

    record = {
        "timestamp": time.time(),
        "action": last_action["action"],
        "reason": reason,
        "current_score": round(score, 4),
        "alternative": alternative,
        "alternative_score_estimate": round(alt_score_estimate, 4),
        "kept_current": chosen_better,
        "directive_strength": round(protection, 4)
    }

    data["last_reasoning"] = record
    data["history"].append(record)
    data["history"] = data["history"][-50:]

    _safe_save(REASON_PATH, data)

    return {
        "status": "reasoning_complete",
        "reasoning": record
    }
