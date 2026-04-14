import json, os

IDENTITY_PATH = "backend/data/identity_continuity.json"
REFLECTION_PATH = "backend/data/reflection_memory.json"

def _load_identity():
    if not os.path.exists(IDENTITY_PATH):
        return None
    with open(IDENTITY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_identity(data):
    with open(IDENTITY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _load_reflection():
    if not os.path.exists(REFLECTION_PATH):
        return None
    with open(REFLECTION_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _clamp(x):
    return max(0.0, min(1.0, x))

def apply_self_correction():
    identity = _load_identity()
    reflection_data = _load_reflection()

    if not identity or not reflection_data:
        return {"status": "missing_data"}

    reflections = reflection_data.get("reflections", [])
    if not reflections:
        return {"status": "no_reflection"}

    latest = reflections[-1]
    judgment = latest.get("judgment", [])

    traits = identity.get("traits", {})

    changes = []

    # --- Correction rules ---
    if "risk_heavy" in judgment:
        traits["risk"] = _clamp(traits.get("risk", 0.5) - 0.03)
        traits["stability"] = _clamp(traits.get("stability", 0.5) + 0.02)
        changes.append("reduce_risk")

    if "low_stability" in judgment:
        traits["stability"] = _clamp(traits.get("stability", 0.5) + 0.03)
        changes.append("increase_stability")

    if "high_exploration" in judgment:
        traits["curiosity"] = _clamp(traits.get("curiosity", 0.5) - 0.01)
        changes.append("temper_exploration")

    if "strong_followthrough" in judgment:
        traits["persistence"] = _clamp(traits.get("persistence", 0.5) + 0.01)
        changes.append("reinforce_persistence")

    identity["traits"] = traits
    _save_identity(identity)

    return {
        "status": "self_corrected",
        "applied": changes,
        "traits": traits
    }
