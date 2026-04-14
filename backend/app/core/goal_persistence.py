import json, os, math

PERSIST_PATH = "backend/data/goal_persistence.json"

def load_persistence():
    if not os.path.exists(PERSIST_PATH):
        return {}
    return json.load(open(PERSIST_PATH, "r"))

def save_persistence(data):
    json.dump(data, open(PERSIST_PATH, "w"), indent=2)

def get_persistence(goal_id):
    data = load_persistence()
    return data.get(goal_id, 0)

def record_goal_outcome(goal_id, won):
    data = load_persistence()

    if goal_id not in data:
        data[goal_id] = 0

    if won:
        # decay faster when winning (prevents dominance lock)
        data[goal_id] = max(0, data[goal_id] - 2)
    else:
        data[goal_id] += 1

    # HARD CAP (prevents runaway obsession)
    data[goal_id] = min(data[goal_id], 10)

    # GLOBAL DECAY (every update weakens old loops)
    for g in list(data.keys()):
        data[g] = max(0, data[g] - 0.1)

    save_persistence(data)
    return data[goal_id]
