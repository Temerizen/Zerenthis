import json
from datetime import datetime
from pathlib import Path

DATA_PATH = Path("backend/data/outcome_memory.json")

def load_data():
    if not DATA_PATH.exists():
        return []
    try:
        raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        return [x for x in raw if isinstance(x, dict)]
    except Exception:
        return []

def save_data(data):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

def log_result(entry):
    if not isinstance(entry, dict):
        print("?? Skipping invalid log entry:", entry)
        return
    data = load_data()
    entry["timestamp"] = datetime.utcnow().isoformat()
    data.append(entry)
    save_data(data)

def score_entry(entry):
    if not isinstance(entry, dict):
        return 0
    return (
        entry.get("views", 0) * 0.1 +
        entry.get("clicks", 0) * 0.5 +
        entry.get("sales", 0) * 5
    )

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
