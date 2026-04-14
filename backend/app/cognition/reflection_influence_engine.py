import json, os

REFLECT_PATH = "backend/data/self_reflection.json"

def _safe_load(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        return default

def run():
    data = _safe_load(REFLECT_PATH, {"last_reflection": None})
    last = data.get("last_reflection")

    if not last:
        return {"status": "no_reflection"}

    summary = last.get("summary", "").lower()
    state = last.get("state", {})

    influence = {
        "pressure": 0.0,
        "risk_modifier": 0.0,
        "strategy_adjustment": None,
        "goal_adjustment": None
    }

    # =========================
    # INTERPRET REFLECTION
    # =========================

    if "misaligned" in summary:
        influence["pressure"] += 0.2
        influence["strategy_adjustment"] = "realign"

    if "uncertain" in summary:
        influence["risk_modifier"] -= 0.1

    if "close to completion" in summary:
        influence["pressure"] += 0.3
        influence["goal_adjustment"] = "finish"

    if "gaining trust" in summary:
        influence["pressure"] += 0.1

    # fallback from numeric state
    if not influence["strategy_adjustment"]:
        if state.get("coherent") is False:
            influence["strategy_adjustment"] = "stabilize"

    return {
        "status": "reflection_influence_active",
        "influence": influence,
        "summary_used": summary
    }
