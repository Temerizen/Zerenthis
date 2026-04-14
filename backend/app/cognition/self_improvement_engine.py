import json, os, time

IMPROVE_PATH = "backend/data/self_improvement.json"
STABILITY_PATH = "backend/data/stability.json"
MEMORY_PATH = "backend/data/memory_depth.json"
REASON_PATH = "backend/data/reasoning.json"
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

def _choose_target(stability, memory, reasoning, directive):
    baseline = stability.get("last_baseline", {})
    canonical = baseline.get("canonical", {})
    flags = baseline.get("flags", {})

    trend = memory.get("trend")
    last_reasoning = reasoning.get("last_reasoning", {})
    directive_obj = directive.get("active_directive")

    last_score = canonical.get("last_score", 0.0) or 0.0
    mission_progress = canonical.get("mission_progress", 0.0) or 0.0
    coherent = flags.get("coherent", False)
    has_mission = flags.get("has_mission", False)
    directive_status = canonical.get("directive_status")
    kept_current = last_reasoning.get("kept_current", True)

    if not has_mission:
        return {
            "component": "mission_continuity",
            "reason": "mission_missing",
            "proposal": "Strengthen mission persistence and recovery guarantees."
        }

    if not coherent:
        return {
            "component": "coherence",
            "reason": "state_misalignment",
            "proposal": "Tighten goal-mission-directive synchronization rules."
        }

    if trend == "declining":
        return {
            "component": "strategy",
            "reason": "declining_performance",
            "proposal": "Refine strategic adjustment thresholds and reduce lag in corrective shifts."
        }

    if trend == "unstable":
        return {
            "component": "memory_reasoning",
            "reason": "unstable_outcomes",
            "proposal": "Deepen memory weighting so recent volatility affects reasoning more strongly."
        }

    if kept_current is False:
        return {
            "component": "reasoning",
            "reason": "reasoning_disagrees_with_action",
            "proposal": "Use reasoning output to influence next-cycle action selection more directly."
        }

    if directive_status == "degraded":
        return {
            "component": "directive",
            "reason": "directive_not_fully_healthy",
            "proposal": "Add directive recovery logic so autonomous protection never degrades silently."
        }

    if last_score < 0.65:
        return {
            "component": "performance",
            "reason": "score_below_target",
            "proposal": "Bias the system toward safer execution until score consistency improves."
        }

    if mission_progress < 0.95:
        return {
            "component": "completion",
            "reason": "mission_not_finished",
            "proposal": "Add mission completion handling and next-mission promotion."
        }

    return {
        "component": "builder_bridge",
        "reason": "system_stable_enough_for_meta_growth",
        "proposal": "Prepare a safe builder bridge so approved self-improvement proposals can become patch plans."
    }

def run():
    improve = _safe_load(IMPROVE_PATH, {"last_proposal": None, "history": []})
    stability = _safe_load(STABILITY_PATH, {"last_baseline": None, "history": []})
    memory = _safe_load(MEMORY_PATH, {"recent_scores": [], "trend": None, "last_pattern": None})
    reasoning = _safe_load(REASON_PATH, {"last_reasoning": None, "history": []})
    directive = _safe_load(AUTO_PATH, {"active_directive": None, "history": []})

    target = _choose_target(stability, memory, reasoning, directive)

    proposal = {
        "timestamp": time.time(),
        "status": "proposal_created",
        "component": target["component"],
        "reason": target["reason"],
        "proposal": target["proposal"],
        "approved": False,
        "applied": False
    }

    improve["last_proposal"] = proposal
    improve["history"].append(proposal)
    improve["history"] = improve["history"][-50:]
    _safe_save(IMPROVE_PATH, improve)

    return {
        "status": "self_improvement_proposed",
        "proposal": proposal
    }
