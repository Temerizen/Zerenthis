import json, os, time

EVOLUTION_PATH = "backend/data/strategy_evolution.json"
STRATEGY_PATH = "backend/data/strategy.json"

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

def _avg(values):
    if not values:
        return 0.5
    return sum(values) / len(values)

def _derive_tendency(avg_score):
    if avg_score >= 0.75:
        return "confident"
    if avg_score >= 0.60:
        return "stable"
    if avg_score >= 0.45:
        return "neutral"
    return "corrective"

def _evolve_name(base_name, tendency, stage):
    if tendency == "confident":
        return f"{base_name}_ascendant_v{stage}"
    if tendency == "stable":
        return f"{base_name}_steady_v{stage}"
    if tendency == "corrective":
        return f"{base_name}_corrective_v{stage}"
    return f"{base_name}_adaptive_v{stage}"

def run(context):
    evo = _safe_load(EVOLUTION_PATH, {
        "current_profile": {
            "name": "default",
            "tendency": "neutral",
            "score_history": [],
            "avg_score": 0.5,
            "evolution_stage": 0
        },
        "history": []
    })

    strategy_data = _safe_load(STRATEGY_PATH, {
        "current_strategy": "default",
        "history": []
    })

    score = float(context.get("score", 0.5))
    current_strategy = strategy_data.get("current_strategy", "default")

    profile = evo.get("current_profile", {})
    score_history = profile.get("score_history", [])
    score_history.append(score)
    score_history = score_history[-10:]

    avg_score = _avg(score_history)
    tendency = _derive_tendency(avg_score)

    previous_tendency = profile.get("tendency", "neutral")
    stage = int(profile.get("evolution_stage", 0))

    if tendency != previous_tendency:
        stage += 1
    elif len(score_history) >= 3 and avg_score >= 0.65:
        stage += 1

    evolved_name = _evolve_name(current_strategy, tendency, stage)

    new_profile = {
        "name": evolved_name,
        "base_strategy": current_strategy,
        "tendency": tendency,
        "score_history": score_history,
        "avg_score": avg_score,
        "evolution_stage": stage,
        "last_updated": time.time()
    }

    evo["current_profile"] = new_profile
    evo["history"].append({
        "timestamp": time.time(),
        "strategy": current_strategy,
        "evolved_name": evolved_name,
        "tendency": tendency,
        "avg_score": avg_score,
        "stage": stage
    })
    evo["history"] = evo["history"][-50:]

    _safe_save(EVOLUTION_PATH, evo)

    return {
        "status": "strategy_evolved",
        "profile": new_profile
    }
