import json
import os
from datetime import datetime

DATA_PATH = "backend/data/outcome_memory.json"

def load_data():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

def log_result(entry):
    data = load_data()
    entry["timestamp"] = str(datetime.utcnow())
    data.append(entry)
    save_data(data)

def score_entry(entry):
    score = 0
    score += entry.get("views", 0) * 0.1
    score += entry.get("clicks", 0) * 0.5
    score += entry.get("sales", 0) * 5
    return score

def get_top_performers():
    data = load_data()
    for d in data:
        d["score"] = score_entry(d)
    return sorted(data, key=lambda x: x["score"], reverse=True)[:5]

def suggest_next_move():
    top = get_top_performers()
    if not top:
        return {"action": "explore", "message": "No data yet"}

    best = top[0]

    return {
        "action": "double_down",
        "niche": best.get("niche"),
        "type": best.get("type"),
        "message": f"Focus on {best.get('niche')} {best.get('type')}"
    }