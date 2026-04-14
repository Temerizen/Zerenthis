import json, os, time

IDENTITY_PATH = "backend/data/identity_consolidation.json"
REINF_PATH = "backend/data/reinforcement.json"
VAL_PATH = "backend/data/validation_feedback.json"
STAB_PATH = "backend/data/stability.json"
STRATEGY_PATH = "backend/data/strategy.json"

def _safe_load(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        return default

def _safe_save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, float(v)))

def run():
    identity = _safe_load(IDENTITY_PATH, {
        "traits": {
            "caution": 0.5,
            "adaptability": 0.5,
            "confidence": 0.5,
            "persistence": 0.5
        },
        "last_identity_update": None,
        "history": []
    })

    reinforcement = _safe_load(REINF_PATH, {"weights": {}, "history": []})
    validation = _safe_load(VAL_PATH, {"last_validation": None, "history": []})
    stability = _safe_load(STAB_PATH, {"last_baseline": None, "history": []})
    strategy = _safe_load(STRATEGY_PATH, {"current_strategy": "default", "history": []})

    traits = identity.get("traits", {})
    caution = _clamp(traits.get("caution", 0.5))
    adaptability = _clamp(traits.get("adaptability", 0.5))
    confidence = _clamp(traits.get("confidence", 0.5))
    persistence = _clamp(traits.get("persistence", 0.5))

    weights = reinforcement.get("weights", {})
    memory_reasoning_weight = _clamp(weights.get("memory_reasoning", 0.5))

    last_validation = validation.get("last_validation") or {}
    decision = last_validation.get("decision", "observe")
    result = last_validation.get("result", "inconclusive")

    baseline = stability.get("last_baseline") or {}
    canonical = baseline.get("canonical") or {}
    overall_score = _clamp(baseline.get("overall_score", 0.5))
    directive_protection = _clamp(canonical.get("directive_protection", 0.5))
    current_strategy = strategy.get("current_strategy", "default")

    # =========================
    # CONSOLIDATION RULES
    # =========================

    # Memory/reasoning reinforcement slowly hardens adaptability
    adaptability = _clamp(adaptability + ((memory_reasoning_weight - 0.5) * 0.10))

    # Validation result shapes confidence
    if decision == "reinforce":
        confidence = _clamp(confidence + 0.08)
    elif decision == "reject":
        confidence = _clamp(confidence - 0.08)
    else:
        confidence = _clamp(confidence + 0.01)

    # Strategy shapes caution / persistence
    if current_strategy == "reduce_risk":
        caution = _clamp(caution + 0.05)
        persistence = _clamp(persistence + 0.01)
    elif current_strategy == "optimize_focus":
        persistence = _clamp(persistence + 0.05)
        caution = _clamp(caution - 0.02)
    elif current_strategy == "increase_efficiency":
        confidence = _clamp(confidence + 0.03)
        persistence = _clamp(persistence + 0.03)

    # Overall score and directive strength stabilize persistence
    persistence = _clamp(persistence + ((overall_score - 0.5) * 0.06))
    confidence = _clamp(confidence + ((directive_protection - 0.5) * 0.04))

    # Build qualitative tendency labels
    tendencies = []
    if caution >= 0.65:
        tendencies.append("cautious")
    if adaptability >= 0.65:
        tendencies.append("adaptive")
    if confidence >= 0.65:
        tendencies.append("confident")
    if persistence >= 0.65:
        tendencies.append("persistent")
    if not tendencies:
        tendencies.append("forming")

    traits = {
        "caution": round(caution, 4),
        "adaptability": round(adaptability, 4),
        "confidence": round(confidence, 4),
        "persistence": round(persistence, 4)
    }

    record = {
        "timestamp": time.time(),
        "traits": traits,
        "tendencies": tendencies,
        "source": {
            "decision": decision,
            "result": result,
            "memory_reasoning_weight": round(memory_reasoning_weight, 4),
            "overall_score": round(overall_score, 4),
            "strategy": current_strategy
        }
    }

    identity["traits"] = traits
    identity["last_identity_update"] = record
    identity["history"].append(record)
    identity["history"] = identity["history"][-100:]

    _safe_save(IDENTITY_PATH, identity)

    return {
        "status": "identity_consolidated",
        "traits": traits,
        "tendencies": tendencies
    }
