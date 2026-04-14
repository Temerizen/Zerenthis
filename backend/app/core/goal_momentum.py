import json, os

PATH = "backend/data/goal_momentum.json"

def load():
    if not os.path.exists(PATH):
        return {}
    try:
        return json.load(open(PATH, "r", encoding="utf-8"))
    except Exception:
        return {}

def save(data):
    json.dump(data, open(PATH, "w", encoding="utf-8"), indent=2)

def get(goal_id):
    data = load()
    return data.get(goal_id, {
        "streak": 0,
        "momentum": 0.0,
        "fatigue": 0.0,
        "wins": 0,
        "last_selected": False
    })

def update(goal_id, won):
    data = load()

    if goal_id not in data:
        data[goal_id] = {
            "streak": 0,
            "momentum": 0.0,
            "fatigue": 0.0,
            "wins": 0,
            "last_selected": False
        }

    # passive decay for everyone, every cycle
    for gid, entry in data.items():
        entry["momentum"] = max(0.0, float(entry.get("momentum", 0.0)) * 0.90)
        entry["fatigue"] = max(0.0, float(entry.get("fatigue", 0.0)) * 0.94)

    entry = data[goal_id]
    was_selected = bool(entry.get("last_selected", False))

    if won:
        entry["wins"] = int(entry.get("wins", 0)) + 1

        # true streak only chains across consecutive wins
        if was_selected:
            entry["streak"] = int(entry.get("streak", 0)) + 1
        else:
            entry["streak"] = 1

        entry["momentum"] = min(1.0, float(entry.get("momentum", 0.0)) + 0.10)
        entry["fatigue"] = min(0.8, float(entry.get("fatigue", 0.0)) + 0.06)
        entry["last_selected"] = True
    else:
        entry["streak"] = 0
        entry["momentum"] = max(0.0, float(entry.get("momentum", 0.0)) * 0.65)
        entry["fatigue"] = max(0.0, float(entry.get("fatigue", 0.0)) - 0.04)
        entry["last_selected"] = False

    save(data)
    return entry
