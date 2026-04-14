import json, os, time

STABILITY_PATH = "backend/data/stability.json"
GOALS_PATH = "backend/data/goals.json"
MISSION_PATH = "backend/data/mission.json"
REALITY_PATH = "backend/data/reality.json"
ADAPT_PATH = "backend/data/adaptation.json"
STRATEGY_PATH = "backend/data/strategy.json"
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

def _safe_save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))

def _round(v):
    if v is None:
        return None
    return round(float(v), 4)

def _compute_normalized_goal_progress(goals_data, active_goal):
    active_progress = active_goal.get("progress", 0.0) if active_goal else 0.0
    history = goals_data.get("history", [])
    best_historical_progress = 0.0
    for item in history:
        if isinstance(item, dict):
            best_historical_progress = max(best_historical_progress, float(item.get("progress", 0.0)))
    return _clamp(max(active_progress, best_historical_progress))

def _phase_label(score):
    if score >= 0.85:
        return "directive_stable"
    if score >= 0.70:
        return "companion_coherent"
    if score >= 0.55:
        return "adaptive_core_online"
    if score >= 0.40:
        return "proto_agency"
    return "bootstrapping"

def run():
    stability = _safe_load(STABILITY_PATH, {"last_baseline": None, "history": []})
    goals = _safe_load(GOALS_PATH, {"active_goals": [], "history": []})
    mission = _safe_load(MISSION_PATH, {"active_mission": None, "history": []})
    reality = _safe_load(REALITY_PATH, {"history": [], "last_outcome": None})
    adaptation = _safe_load(ADAPT_PATH, {"last_adjustment": None, "history": []})
    strategy = _safe_load(STRATEGY_PATH, {"current_strategy": "default", "history": []})
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
    profile = evolution.get("current_profile")
    last_coherence = coherence.get("last_check")
    last_correction = correction.get("last_correction")
    active_directive = autonomous.get("active_directive")

    goal_commitment = float(active_goal.get("commitment", 0.0)) if active_goal else 0.0
    goal_progress = _compute_normalized_goal_progress(goals, active_goal)
    mission_progress = float(active_mission.get("progress", 0.0)) if active_mission else 0.0
    last_score = float(last_outcome.get("score", 0.0)) if last_outcome else 0.0
    directive_protection = float(active_directive.get("protection", 0.0)) if active_directive else 0.0

    coherence_ok = 1.0 if last_coherence and last_coherence.get("action") == "aligned" else 0.0
    correction_ok = 1.0 if last_correction and last_correction.get("action") in ("no_change", "goal_aligned_to_mission") else 0.0

    overall_score = _clamp(
        (goal_commitment * 0.20) +
        (goal_progress * 0.20) +
        (mission_progress * 0.20) +
        (last_score * 0.15) +
        (directive_protection * 0.15) +
        (coherence_ok * 0.05) +
        (correction_ok * 0.05)
    )

    baseline = {
        "timestamp": time.time(),
        "phase": _phase_label(overall_score),
        "overall_score": _round(overall_score),
        "canonical": {
            "goal_type": active_goal.get("type") if active_goal else None,
            "goal_commitment": _round(goal_commitment),
            "goal_progress_normalized": _round(goal_progress),
            "mission_id": active_mission.get("id") if active_mission else None,
            "mission_goal_type": active_mission.get("goal_type") if active_mission else None,
            "mission_progress": _round(mission_progress),
            "last_score": _round(last_score),
            "last_adjustment_action": last_adjustment.get("action") if last_adjustment else None,
            "strategy": current_strategy,
            "strategy_profile": profile.get("name") if profile else None,
            "strategy_tendency": profile.get("tendency") if profile else None,
            "strategy_stage": profile.get("evolution_stage") if profile else None,
            "coherence_action": last_coherence.get("action") if last_coherence else None,
            "correction_action": last_correction.get("action") if last_correction else None,
            "directive_priority": _round(active_directive.get("priority")) if active_directive else None,
            "directive_protection": _round(directive_protection),
            "directive_status": active_directive.get("status") if active_directive else None
        },
        "flags": {
            "has_goal": active_goal is not None,
            "has_mission": active_mission is not None,
            "has_directive": active_directive is not None,
            "coherent": coherence_ok == 1.0,
            "self_correcting": correction_ok == 1.0
        }
    }

    stability["last_baseline"] = baseline
    stability["history"].append(baseline)
    stability["history"] = stability["history"][-50:]
    _safe_save(STABILITY_PATH, stability)

    return {
        "status": "baseline_recorded",
        "baseline": baseline
    }
