import json, os, time

IDENTITY_PATH = "backend/data/identity_continuity.json"
VALUES_PATH = "backend/data/value_hierarchy.json"

DEFAULT_VALUES = {
    "exploration": 0.7,
    "stability": 0.7,
    "persistence": 0.65,
    "efficiency": 0.6
}

def _load_identity():
    if not os.path.exists(IDENTITY_PATH):
        return {"traits": {}}
    with open(IDENTITY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _load_values():
    if not os.path.exists(VALUES_PATH):
        return {
            "values": DEFAULT_VALUES,
            "history": []
        }
    with open(VALUES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_values(data):
    with open(VALUES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def evaluate_values():
    identity = _load_identity()
    data = _load_values()

    traits = identity.get("traits", {})
    values = data.get("values", DEFAULT_VALUES)

    curiosity = float(traits.get("curiosity", 0.5))
    stability_trait = float(traits.get("stability", 0.5))
    risk = float(traits.get("risk", 0.5))
    persistence_trait = float(traits.get("persistence", 0.5))

    scores = {
        "exploration": round((curiosity * 0.7) + (risk * 0.3), 3),
        "stability": round((stability_trait * 0.8) + ((1 - risk) * 0.2), 3),
        "persistence": round(persistence_trait, 3),
        "efficiency": round((persistence_trait * 0.6) + (stability_trait * 0.4), 3),
    }

    weighted_scores = {
        key: round(scores[key] * float(values.get(key, 0.5)), 3)
        for key in scores
    }

    dominant_value = max(weighted_scores, key=weighted_scores.get)

    snapshot = {
        "timestamp": time.time(),
        "scores": scores,
        "weighted_scores": weighted_scores,
        "dominant_value": dominant_value
    }

    data["history"].append(snapshot)
    if len(data["history"]) > 200:
        data["history"] = data["history"][-200:]

    _save_values(data)

    return {
        "status": "value_hierarchy_evaluated",
        "scores": scores,
        "weighted_scores": weighted_scores,
        "dominant_value": dominant_value,
        "history_size": len(data["history"])
    }
