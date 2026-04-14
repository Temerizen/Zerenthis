import os, json, time

BASE = "backend/data/performance_log.json"

def load():
    if not os.path.exists(BASE):
        return {"history": [], "best_score": None}
    with open(BASE, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save(data):
    os.makedirs(os.path.dirname(BASE), exist_ok=True)
    with open(BASE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def record(score):
    data = load()
    entry = {
        "score": score,
        "timestamp": time.time()
    }
    data["history"].append(entry)

    if data["best_score"] is None or score > data["best_score"]:
        data["best_score"] = score

    save(data)
    return data

def get_best():
    return load().get("best_score")

def recent(n=5):
    return load().get("history", [])[-n:]

