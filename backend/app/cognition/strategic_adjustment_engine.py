import json, os, time

ADJUST_PATH = "backend/data/strategic_adjustment.json"
MEM_PATH = "backend/data/memory_depth.json"
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

def _choose_strategy(current, trend):
    if trend == "declining":
        if current == "default":
            return "reduce_risk"
        if current == "reduce_risk":
            return "optimize_focus"
        if current == "optimize_focus":
            return "increase_efficiency"
        return "reduce_risk"

    if trend == "improving":
        if current == "default":
            return "optimize_focus"
        if current == "optimize_focus":
            return "increase_efficiency"
        return current

    if trend == "unstable":
        return "reduce_risk"

    return current

def run():
    adjust_data = _safe_load(ADJUST_PATH, {"last_adjustment": None, "history": []})
    memory = _safe_load(MEM_PATH, {"recent_scores": [], "trend": None, "last_pattern": None})
    strategy = _safe_load(STRATEGY_PATH, {"current_strategy": "default", "history": []})

    trend = memory.get("trend")
    current_strategy = strategy.get("current_strategy", "default")
    new_strategy = current_strategy
    action = "kept"

    if trend in ("declining", "unstable", "improving"):
        candidate = _choose_strategy(current_strategy, trend)
        if candidate != current_strategy:
            new_strategy = candidate
            strategy["history"].append({
                "timestamp": time.time(),
                "from": current_strategy,
                "to": new_strategy,
                "reason": f"memory_trend:{trend}"
            })
            strategy["current_strategy"] = new_strategy
            _safe_save(STRATEGY_PATH, strategy)
            action = "shifted"

    record = {
        "timestamp": time.time(),
        "trend": trend,
        "previous_strategy": current_strategy,
        "new_strategy": new_strategy,
        "action": action
    }

    adjust_data["last_adjustment"] = record
    adjust_data["history"].append(record)
    adjust_data["history"] = adjust_data["history"][-50:]
    _safe_save(ADJUST_PATH, adjust_data)

    return {
        "status": "strategic_adjustment_applied",
        "trend": trend,
        "action": action,
        "strategy": new_strategy
    }
