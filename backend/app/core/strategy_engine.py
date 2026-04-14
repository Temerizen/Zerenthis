import json, os, time

PATH = "backend/data/strategy_state.json"

def load():
    if not os.path.exists(PATH):
        return {
            "current_strategy": [],
            "history": [],
            "last_goal": None,
            "step_index": 0
        }
    try:
        return json.load(open(PATH, "r", encoding="utf-8"))
    except Exception:
        return {
            "current_strategy": [],
            "history": [],
            "last_goal": None,
            "step_index": 0
        }

def save(data):
    json.dump(data, open(PATH, "w", encoding="utf-8"), indent=2)

def get_next_step(goal_id):
    data = load()

    # If new goal, start new chain
    if data.get("last_goal") != goal_id:
        data["current_strategy"] = []
        data["step_index"] = 0
        data["last_goal"] = goal_id

    steps = data.get("current_strategy", [])

    if data["step_index"] < len(steps):
        step = steps[data["step_index"]]
        data["step_index"] += 1
        save(data)
        return step

    return None

def record_step(goal_id, task):
    data = load()

    if data.get("last_goal") != goal_id:
        data["current_strategy"] = []
        data["step_index"] = 0
        data["last_goal"] = goal_id

    data["current_strategy"].append({
        "task": task,
        "ts": time.time()
    })

    save(data)
