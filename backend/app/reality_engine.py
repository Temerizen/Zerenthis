import os, json
from datetime import datetime

DATA_PATH = "backend/data/reality_feedback.json"

def _now():
    return datetime.utcnow().isoformat()+"Z"

def load():
    if not os.path.exists(DATA_PATH):
        return []
    try:
        return json.load(open(DATA_PATH,"r"))
    except:
        return []

def save(data):
    json.dump(data, open(DATA_PATH,"w"), indent=2)

def add_feedback(entry):
    data = load()
    entry["timestamp"] = _now()
    data.insert(0, entry)
    data = data[:200]
    save(data)
    return entry

def get_feedback(limit=20):
    return load()[:limit]

def score_signal(entry):
    score = 0

    views = entry.get("views",0)
    likes = entry.get("likes",0)
    sales = entry.get("sales",0)

    if views > 1000: score += 2
    if views > 10000: score += 2

    if likes > 50: score += 2
    if likes > 200: score += 2

    if sales > 0: score += 3

    return min(score,10)
