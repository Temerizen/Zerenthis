import json, os, time

VALUES_PATH = "backend/data/value_hierarchy.json"

def _load():
    if not os.path.exists(VALUES_PATH):
        return {
            "values": {
                "exploration": 0.7,
                "stability": 0.7,
                "persistence": 0.65,
                "efficiency": 0.6
            },
            "history": []
        }
    with open(VALUES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data):
    with open(VALUES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def reinforce_values(context: dict | None = None):
    context = context or {}
    data = _load()

    values = data.get("values", {})
    outcome = (context.get("execution_state") or {}).get("status")

    delta = 0.02

    if outcome == "execution_aligned":
        values["exploration"] = min(1.0, values.get("exploration", 0.5) + delta)
        values["persistence"] = min(1.0, values.get("persistence", 0.5) + delta)

    else:
        values["stability"] = min(1.0, values.get("stability", 0.5) + delta)
        values["efficiency"] = min(1.0, values.get("efficiency", 0.5) + delta)

    snapshot = {
        "timestamp": time.time(),
        "values": values.copy(),
        "outcome": outcome
    }

    data["values"] = values
    data["history"].append(snapshot)

    if len(data["history"]) > 200:
        data["history"] = data["history"][-200:]

    _save(data)

    return {
        "status": "values_reinforced",
        "values": values,
        "last_outcome": outcome
    }
