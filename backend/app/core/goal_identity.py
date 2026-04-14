import json, os, time

PATH = "backend/data/goal_identity_state.json"

def load():
    if not os.path.exists(PATH):
        return {
            "dominant_goal_type": None,
            "type_weights": {},
            "history": [],
            "updated_at": None
        }
    try:
        return json.load(open(PATH, "r", encoding="utf-8"))
    except Exception:
        return {
            "dominant_goal_type": None,
            "type_weights": {},
            "history": [],
            "updated_at": None
        }

def save(data):
    json.dump(data, open(PATH, "w", encoding="utf-8"), indent=2)

def get_bias(goal_type):
    data = load()
    weights = data.get("type_weights", {}) or {}
    return float(weights.get(goal_type, 0.0) or 0.0)

def record(goal_type, goal_id):
    data = load()
    weights = data.setdefault("type_weights", {})
    history = data.setdefault("history", [])

    # decay all identity weights slightly
    for k in list(weights.keys()):
        weights[k] = max(0.0, float(weights.get(k, 0.0)) * 0.96)

    weights[goal_type] = min(0.6, float(weights.get(goal_type, 0.0)) + 0.08)

    history.append({
        "goal_type": goal_type,
        "goal_id": goal_id,
        "ts": time.time()
    })
    data["history"] = history[-30:]

    if weights:
        data["dominant_goal_type"] = max(weights.items(), key=lambda kv: kv[1])[0]
    data["updated_at"] = time.time()

    save(data)
    return data
