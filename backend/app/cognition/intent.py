import time, json, os

INTENT_PATH = "backend/data/intent_memory.json"

def _load():
    if not os.path.exists(INTENT_PATH):
        return {"intents": []}
    with open(INTENT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data):
    with open(INTENT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def form_intent(context: dict | None = None):
    context = context or {}

    pattern_bias = context.get("pattern_bias", {}) or {}
    tension_bias = context.get("tension_bias", {}) or {}
    self_model = context.get("self_model_state", {}) or {}
    goal_state = context.get("goal_state", {}) or {}

    confidence = float(self_model.get("confidence", 0.5))
    mode = self_model.get("mode", "learning")
    active_goal = goal_state.get("active_goal", "unknown")

    intent = None
    reason = []

    # Tension-driven intent (strongest)
    if tension_bias.get("bias") == "variation_momentum":
        intent = "expand_behavior"
        reason.append("tension_variation_momentum")

    elif tension_bias.get("bias") == "repetition_momentum":
        intent = "break_loop"
        reason.append("tension_repetition_pressure")

    # Pattern-driven intent
    elif pattern_bias.get("bias") == "explore_variation":
        intent = "expand_behavior"
        reason.append("pattern_variation")

    elif pattern_bias.get("bias") == "break_repetition":
        intent = "escape_loop"
        reason.append("pattern_repetition")

    # Self-driven fallback
    else:
        if confidence > 0.8:
            intent = "optimize"
            reason.append("high_confidence_self_direction")
        else:
            intent = "explore"
            reason.append("default_exploration")

    return {
        "intent": intent,
        "reason": reason,
        "confidence": round(confidence, 3),
        "mode": mode,
        "goal": active_goal
    }

def update_intent_memory(intent_state):
    data = _load()
    intents = data.get("intents", [])

    entry = {
        "intent": intent_state.get("intent"),
        "reason": intent_state.get("reason"),
        "confidence": intent_state.get("confidence"),
        "timestamp": time.time()
    }

    intents.append(entry)
    intents = intents[-50:]

    data["intents"] = intents
    _save(data)

    return {
        "status": "intent_recorded",
        "latest": entry,
        "count": len(intents)
    }
