import json, os, time

VAL_PATH = "backend/data/validation_feedback.json"
REINF_PATH = "backend/data/reinforcement.json"

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

def run():
    val = _safe_load(VAL_PATH, {})
    reinf = _safe_load(REINF_PATH, {"weights": {}, "history": []})

    last = val.get("last_validation")
    if not last or last.get("status") != "validated":
        return {"status": "no_validation"}

    component = last.get("execution_component", "unknown")
    decision = last.get("decision", "observe")

    weights = reinf.get("weights", {})

    current = weights.get(component, 0.5)

    if decision == "reinforce":
        current += 0.1
    elif decision == "reject":
        current -= 0.1
    else:
        current += 0.02  # small learning drift

    # clamp
    current = max(0.0, min(1.0, current))

    weights[component] = current

    record = {
        "timestamp": time.time(),
        "component": component,
        "decision": decision,
        "new_weight": current
    }

    reinf["weights"] = weights
    reinf["history"].append(record)
    reinf["history"] = reinf["history"][-100:]

    _safe_save(REINF_PATH, reinf)

    return {
        "status": "reinforced",
        "component": component,
        "weight": current,
        "decision": decision
    }
