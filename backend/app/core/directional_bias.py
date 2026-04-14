from backend.app.core.goal_types import classify_goal
from backend.app.core.directional_weights import get_directional_weights
from backend.app.core.goal_persistence import get_persistence, record_goal_outcome
from backend.app.core.goal_momentum import get as get_momentum, update as update_momentum
from backend.app.core.goal_identity import get_bias as get_identity_bias, record as record_identity
from backend.app.core.goal_pattern_memory import get_bias as get_pattern_bias, record as record_pattern

def _priority_value(goal):
    raw = goal.get("priority", 0)
    if isinstance(raw, (int, float)):
        return float(raw)

    text = str(raw).strip().lower()
    mapping = {
        "critical": 1.0,
        "high": 0.85,
        "medium": 0.55,
        "normal": 0.5,
        "low": 0.25,
    }
    return mapping.get(text, 0.0)

def _type_bonus(goal_type):
    return {
        "expansion": 0.18,
        "optimization": 0.10,
        "maintenance": 0.06,
        "recovery": 0.08,
    }.get(goal_type, 0.0)

def _goal_family(goal_id):
    gid = str(goal_id or "").lower()
    if "_" in gid:
        return "_".join(gid.split("_")[:2])
    return gid

def _tiny_spread(goal_id):
    gid = str(goal_id or "")
    return (sum(ord(c) for c in gid) % 17) / 1000.0

def _streak_bonus(streak):
    s = int(streak or 0)
    return min(0.25, s * 0.03)

def compute_directional_score(goal, system_state="stable"):
    gid = goal.get("goal_id") or goal.get("id") or "unknown_goal"
    goal_type = classify_goal(gid)
    weights = get_directional_weights(system_state)

    persistence = float(get_persistence(gid) or 0)
    momentum_data = get_momentum(gid)
    momentum = float(momentum_data.get("momentum", 0.0))
    streak = int(momentum_data.get("streak", 0))
    fatigue = float(momentum_data.get("fatigue", 0.0))
    identity_bias = float(get_identity_bias(goal_type) or 0.0)
    pattern_bias = float(get_pattern_bias(goal) or 0.0)

    base_score = goal.get("score", 0)
    try:
        base_score = float(base_score or 0)
    except Exception:
        base_score = 0.0

    if base_score <= 0:
        base_score = _priority_value(goal)

    weighted = base_score * float(weights.get(goal_type, 1.0))
    boosted = weighted

    boosted += _type_bonus(goal_type)
    boosted += persistence * 0.05

    if goal_type == "expansion":
        boosted += 0.12
        if persistence < 1:
            boosted += 0.18

    boosted += momentum
    boosted += _streak_bonus(streak)
    boosted += identity_bias
    boosted += pattern_bias * 0.5
    boosted -= fatigue
    boosted += _tiny_spread(gid)

    return {
        "goal_id": gid,
        "goal_type": goal_type,
        "base_score": base_score,
        "persistence": persistence,
        "momentum": round(momentum, 6),
        "streak": streak,
        "fatigue": round(fatigue, 6),
        "identity_bias": round(identity_bias, 6),
        "score": round(boosted, 6)
    }

def choose_best_goal(goals, system_state="stable"):
    scored = []
    family_counts = {}

    for g in goals:
        if not isinstance(g, dict):
            continue

        result = compute_directional_score(g, system_state)

        goal = dict(g)
        goal["goal_type"] = result["goal_type"]
        goal["persistence"] = result["persistence"]
        goal["base_score"] = result["base_score"]
        goal["momentum"] = result["momentum"]
        goal["streak"] = result["streak"]
        goal["fatigue"] = result["fatigue"]
        goal["identity_bias"] = result["identity_bias"]
        goal["score"] = result["score"]

        fam = _goal_family(result["goal_id"])
        goal["_goal_family"] = fam

        family_counts[fam] = family_counts.get(fam, 0) + 1
        scored.append(goal)

    for g in scored:
        fam = g["_goal_family"]
        if family_counts[fam] > 1:
            penalty = (family_counts[fam] - 1) * 0.035
            g["score"] -= penalty
            g["_family_penalty"] = penalty

    scored.sort(key=lambda x: x["score"], reverse=True)

    # context-aware switching:
    # tired winner + close challenger = allow switch
    if len(scored) >= 2:
        best = scored[0]
        second = scored[1]
        best_score = float(best.get("score", 0.0))
        second_score = float(second.get("score", 0.0))
        best_fatigue = float(best.get("fatigue", 0.0))

        if best_fatigue >= 0.32 and second_score >= best_score * 0.95:
            scored[0], scored[1] = scored[1], scored[0]

    chosen = scored[0] if scored else None

    if chosen:
        chosen_id = chosen.get("goal_id") or chosen.get("id")
        chosen_type = chosen.get("goal_type") or classify_goal(chosen_id)

        for g in scored:
            gid = g.get("goal_id") or g.get("id")
            won = (gid == chosen_id)
            record_goal_outcome(gid, won)
            update_momentum(gid, won)

        record_identity(chosen_type, chosen_id)
        record_pattern(chosen, chosen.get("score", 0))

    return {
        "selected_goal": chosen,
        "ranked_goals": scored
    }

