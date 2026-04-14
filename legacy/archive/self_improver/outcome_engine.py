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

def suggest_next_move():
    data = load_data()

    if not data:
        return {"suggestion": "No data yet. Generate content first."}

    latest = data[-1]
    score = latest.get("score", 0)

    if score < 5:
        suggestion = "Improve hook and title"
    elif score < 8:
        suggestion = "Improve content depth and clarity"
    else:
        suggestion = "Scale this content and create variations"

    result = {
        "score": score,
        "suggestion": suggestion
    }

    print("Next move:", result)
    return result

def evaluate_and_improve():
    decision = suggest_next_move()
    return {"ok": True, "effect": decision["suggestion"]}
