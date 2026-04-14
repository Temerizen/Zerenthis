from backend.app.cognition.patterns import _load as load_patterns
from backend.app.cognition.tension import get_tension_bias

def pattern_bias_decision(context: dict | None = None):
    context = context or {}
    data = load_patterns()
    patterns = data.get("patterns", [])

    goal_state = context.get("goal_state", {}) or {}
    self_model_state = context.get("self_model_state", {}) or {}
    meta_state = context.get("meta_state", {}) or {}

    active_goal = goal_state.get("active_goal", "unknown")
    confidence = float(self_model_state.get("confidence", 0.5))
    mode = self_model_state.get("mode", "learning")
    history_count = meta_state.get("history", 0)

    tension_bias = get_tension_bias()

    if not patterns:
        return {
            "bias": tension_bias.get("bias"),
            "conflict": False,
            "winner": None,
            "arbitration": "tension_only",
            "tension_bias": tension_bias
        }

    top = patterns[:5]

    repetition_weight = round(sum(
        p.get("weight", 0) for p in top
        if p.get("type") == "repetition"
    ), 3)

    variation_weight = round(sum(
        p.get("weight", 0) for p in top
        if p.get("type") == "variation"
    ), 3)

    conflict = repetition_weight >= 1.5 and variation_weight >= 1.5

    stability_pressure = 0.0
    if confidence < 0.65:
        stability_pressure += 1.0
    if mode in ("learning", "adapting"):
        stability_pressure += 0.5
    if active_goal in ("stabilization", "risk_reduction", "safe_progression"):
        stability_pressure += 1.0
    if history_count > 50:
        stability_pressure += 0.25
    stability_pressure = round(stability_pressure, 3)

    if conflict:
        if variation_weight > repetition_weight:
            chosen_bias = "explore_variation"
            chosen_reason = "pattern_conflict_resolved_variation"
            chosen_weight = variation_weight
            opposing_weight = repetition_weight
            winner = "variation"
        elif repetition_weight > variation_weight:
            chosen_bias = "break_repetition"
            chosen_reason = "pattern_conflict_resolved_repetition"
            chosen_weight = repetition_weight
            opposing_weight = variation_weight
            winner = "repetition"
        else:
            return {
                "bias": "balanced_tension",
                "reason": "pattern_conflict_tie",
                "confidence": 0.5,
                "weight": repetition_weight,
                "opposing_weight": variation_weight,
                "conflict": True,
                "winner": "tie",
                "arbitration": "tie",
                "tension_bias": tension_bias
            }

        if chosen_bias == "explore_variation" and stability_pressure >= 1.5:
            return {
                "bias": "cautious_explore",
                "reason": "meta_priority_stability_override",
                "confidence": min(round(chosen_weight / 5, 2), 1.0),
                "weight": chosen_weight,
                "opposing_weight": opposing_weight,
                "conflict": True,
                "winner": winner,
                "stability_pressure": stability_pressure,
                "arbitration": "stability_override",
                "tension_bias": tension_bias
            }

        return {
            "bias": chosen_bias,
            "reason": chosen_reason,
            "confidence": min(round(chosen_weight / 5, 2), 1.0),
            "weight": chosen_weight,
            "opposing_weight": opposing_weight,
            "conflict": True,
            "winner": winner,
            "stability_pressure": stability_pressure,
            "arbitration": "pattern_priority",
            "tension_bias": tension_bias
        }

    # no active conflict, but past tension can still bend behavior
    if tension_bias.get("bias") == "variation_momentum":
        return {
            "bias": "cautious_explore" if stability_pressure >= 1.5 else "explore_variation",
            "reason": "persistent_variation_tension",
            "confidence": min(round(tension_bias.get("strength", 0) / 5, 2), 1.0),
            "weight": tension_bias.get("strength", 0),
            "conflict": False,
            "winner": "variation",
            "stability_pressure": stability_pressure,
            "arbitration": "tension_memory",
            "tension_bias": tension_bias
        }

    if tension_bias.get("bias") == "repetition_momentum":
        return {
            "bias": "break_repetition",
            "reason": "persistent_repetition_tension",
            "confidence": min(round(tension_bias.get("strength", 0) / 5, 2), 1.0),
            "weight": tension_bias.get("strength", 0),
            "conflict": False,
            "winner": "repetition",
            "stability_pressure": stability_pressure,
            "arbitration": "tension_memory",
            "tension_bias": tension_bias
        }

    if repetition_weight >= 3:
        return {
            "bias": "break_repetition",
            "reason": "weighted_repetition_pattern",
            "confidence": min(round(repetition_weight / 5, 2), 1.0),
            "weight": repetition_weight,
            "conflict": False,
            "winner": "repetition",
            "stability_pressure": stability_pressure,
            "arbitration": "pattern_priority",
            "tension_bias": tension_bias
        }

    if variation_weight >= 3:
        if stability_pressure >= 1.5:
            return {
                "bias": "cautious_explore",
                "reason": "meta_priority_stability_override",
                "confidence": min(round(variation_weight / 5, 2), 1.0),
                "weight": variation_weight,
                "conflict": False,
                "winner": "variation",
                "stability_pressure": stability_pressure,
                "arbitration": "stability_override",
                "tension_bias": tension_bias
            }

        return {
            "bias": "explore_variation",
            "reason": "weighted_variation_pattern",
            "confidence": min(round(variation_weight / 5, 2), 1.0),
            "weight": variation_weight,
            "conflict": False,
            "winner": "variation",
            "stability_pressure": stability_pressure,
            "arbitration": "pattern_priority",
            "tension_bias": tension_bias
        }

    return {
        "bias": None,
        "conflict": False,
        "winner": None,
        "stability_pressure": stability_pressure,
        "arbitration": "no_priority_trigger",
        "tension_bias": tension_bias
    }
