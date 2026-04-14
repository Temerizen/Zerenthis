import json, os, time

STATE_PATH = "backend/data/loop_state.json"
COOLDOWN_SECONDS = 20

def _load():
    if not os.path.exists(STATE_PATH):
        return {
            "last_self_run": 0,
            "self_runs": 0,
            "cooldown_seconds": COOLDOWN_SECONDS
        }
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def evaluate_self_initiation(context: dict | None = None):
    context = context or {}
    data = _load()

    now = time.time()
    last_self_run = float(data.get("last_self_run", 0))
    cooldown = int(data.get("cooldown_seconds", COOLDOWN_SECONDS))
    elapsed = now - last_self_run

    intent_state = context.get("intent_state", {}) or {}
    tension_bias = context.get("tension_bias", {}) or {}
    self_model_state = context.get("self_model_state", {}) or {}

    intent = intent_state.get("intent")
    confidence = float(self_model_state.get("confidence", 0.5))
    tension_strength = float(tension_bias.get("strength", 0) or 0)

    should_run = False
    reasons = []

    if elapsed < cooldown:
        return {
            "should_self_run": False,
            "reason": ["cooldown_active"],
            "seconds_until_ready": round(cooldown - elapsed, 2),
            "cooldown_seconds": cooldown,
            "self_runs": data.get("self_runs", 0)
        }

    if intent in ("expand_behavior", "break_loop", "escape_loop", "optimize"):
        should_run = True
        reasons.append(f"intent:{intent}")

    if tension_strength >= 1.5:
        should_run = True
        reasons.append("tension_pressure")

    if confidence >= 0.9:
        should_run = True
        reasons.append("high_confidence")

    return {
        "should_self_run": should_run,
        "reason": reasons or ["insufficient_drive"],
        "seconds_until_ready": 0,
        "cooldown_seconds": cooldown,
        "self_runs": data.get("self_runs", 0)
    }

def record_self_run():
    data = _load()
    data["last_self_run"] = time.time()
    data["self_runs"] = int(data.get("self_runs", 0)) + 1
    _save(data)
    return {
        "status": "self_run_recorded",
        "last_self_run": data["last_self_run"],
        "self_runs": data["self_runs"]
    }
