import json, os

IDENTITY_PATH = "backend/data/identity_consolidation.json"

def _safe_load(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        return default

def run(context=None):
    identity = _safe_load(IDENTITY_PATH, {})
    traits = identity.get("traits", {})

    caution = traits.get("caution", 0.5)
    adaptability = traits.get("adaptability", 0.5)
    confidence = traits.get("confidence", 0.5)
    persistence = traits.get("persistence", 0.5)

    influence = {
        "risk_bias": 0.0,
        "decision_bias": 0.0,
        "strategy_bias": "neutral",
        "commitment_bias": 0.0
    }

    # =========================
    # INFLUENCE RULES
    # =========================

    # Confidence increases decisiveness
    influence["decision_bias"] += (confidence - 0.5) * 0.6

    # Persistence resists switching
    influence["commitment_bias"] += (persistence - 0.5) * 0.7

    # Caution affects risk
    influence["risk_bias"] -= (caution - 0.5) * 0.8

    # Adaptability affects strategy switching
    if adaptability > 0.6:
        influence["strategy_bias"] = "adaptive"
    elif persistence > 0.65:
        influence["strategy_bias"] = "stable"
    elif caution > 0.65:
        influence["strategy_bias"] = "conservative"

    return {
        "status": "identity_influence_active",
        "influence": influence,
        "traits": traits
    }
