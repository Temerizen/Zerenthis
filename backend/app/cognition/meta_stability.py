import json, os, time

IDENTITY_PATH = "backend/data/identity_continuity.json"
STABILITY_PATH = "backend/data/meta_stability.json"

DEFAULT_BANDS = {
    "curiosity": {"target": 0.62, "min": 0.45, "max": 0.78},
    "stability": {"target": 0.58, "min": 0.45, "max": 0.75},
    "risk": {"target": 0.48, "min": 0.30, "max": 0.68},
    "persistence": {"target": 0.60, "min": 0.45, "max": 0.82}
}

def _load_identity():
    if not os.path.exists(IDENTITY_PATH):
        return None
    with open(IDENTITY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_identity(data):
    with open(IDENTITY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _load_stability():
    if not os.path.exists(STABILITY_PATH):
        return {
            "bands": DEFAULT_BANDS,
            "history": []
        }
    with open(STABILITY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_stability(data):
    with open(STABILITY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _clamp(x):
    return max(0.0, min(1.0, x))

def apply_meta_stability():
    identity = _load_identity()
    stability = _load_stability()

    if not identity:
        return {"status": "missing_identity"}

    traits = identity.get("traits", {})
    bands = stability.get("bands", DEFAULT_BANDS)

    adjustments = {}

    for trait, rules in bands.items():
        value = float(traits.get(trait, 0.5))
        target = float(rules.get("target", 0.5))
        min_v = float(rules.get("min", 0.0))
        max_v = float(rules.get("max", 1.0))

        original = value

        if value < min_v:
            value = min(value + 0.02, target)
        elif value > max_v:
            value = max(value - 0.02, target)
        else:
            # gentle damping toward target
            if value < target - 0.03:
                value += 0.01
            elif value > target + 0.03:
                value -= 0.01

        value = round(_clamp(value), 3)
        traits[trait] = value

        delta = round(value - original, 3)
        if delta != 0:
            adjustments[trait] = delta

    identity["traits"] = traits
    _save_identity(identity)

    snapshot = {
        "timestamp": time.time(),
        "traits": traits.copy(),
        "adjustments": adjustments
    }
    stability["history"].append(snapshot)
    if len(stability["history"]) > 200:
        stability["history"] = stability["history"][-200:]

    _save_stability(stability)

    return {
        "status": "meta_stability_applied",
        "traits": traits,
        "adjustments": adjustments,
        "history_size": len(stability["history"])
    }
