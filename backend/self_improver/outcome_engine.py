import os
import json
from datetime import datetime

DATA_PATH = "backend/data/performance_log.json"

def load_data():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save_data(data):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

def log_result(entry):
    data = load_data()
    entry["timestamp"] = str(datetime.utcnow())
    data.append(entry)
    save_data(data)
    print("Logged result:", entry)
    return {"ok": True}

def evaluate_and_improve():
    data = load_data()

    if not data:
        print("No performance data yet.")
        return {"ok": False}

    latest = data[-1]
    score = latest.get("score", 0)

    print(f"Evaluating score: {score}")

    if score < 5:
        action = "Improve hook and title"
    elif score < 8:
        action = "Improve content depth"
    else:
        action = "Scale this content"

    result = {
        "score": score,
        "action": action
    }

    print("Decision:", result)

    data.append(result)
    save_data(data)

    return {"ok": True, "effect": action}
