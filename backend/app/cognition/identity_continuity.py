import json, os, time

IDENTITY_PATH = "backend/data/identity_continuity.json"

DEFAULT = {
    "traits": {
        "curiosity": 0.5,
        "stability": 0.5,
        "risk": 0.5,
        "persistence": 0.5
    },
    "history": []
}

def _load():
    if not os.path.exists(IDENTITY_PATH):
        return {
            "traits": DEFAULT["traits"].copy(),
            "history": []
        }
    with open(IDENTITY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data):
    with open(IDENTITY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _clamp(x):
    return max(0.0, min(1.0, x))

def update_identity(context: dict | None = None):
    context = context or {}
    data = _load()

    traits = data.get("traits", DEFAULT["traits"].copy())
    history = data.get("history", [])

    intent = (context.get("intent_state") or {}).get("intent")
    confidence = float((context.get("self_model_state") or {}).get("confidence", 0.5))
    action = (context.get("decision_state") or {}).get("action")

    if intent == "expand_behavior":
        traits["curiosity"] = _clamp(traits["curiosity"] + 0.02)
        traits["risk"] = _clamp(traits["risk"] + 0.015)

    if intent in ("break_loop", "escape_loop"):
        traits["curiosity"] = _clamp(traits["curiosity"] + 0.03)
        traits["stability"] = _clamp(traits["stability"] - 0.02)

    if intent == "optimize":
        traits["stability"] = _clamp(traits["stability"] + 0.02)
        traits["persistence"] = _clamp(traits["persistence"] + 0.015)

    if confidence > 0.9:
        traits["persistence"] = _clamp(traits["persistence"] + 0.01)

    if action == "branch_and_explore":
        traits["curiosity"] = _clamp(traits["curiosity"] + 0.01)

    snapshot = {
        "timestamp": time.time(),
        "traits": traits.copy(),
        "intent": intent,
        "action": action,
        "confidence": confidence
    }

    history.append(snapshot)
    if len(history) > 200:
        history = history[-200:]

    data["traits"] = traits
    data["history"] = history
    _save(data)

    return {
        "status": "identity_updated",
        "traits": traits,
        "last_intent": intent,
        "history_size": len(history)
    }

def get_identity():
    data = _load()
    return {
        "traits": data.get("traits", {}),
        "history_size": len(data.get("history", []))
    }
