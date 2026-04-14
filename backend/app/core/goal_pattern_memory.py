import json, os, time

PATH = "backend/data/goal_pattern_memory.json"

def load():
    if not os.path.exists(PATH):
        return {}
    try:
        return json.load(open(PATH, "r", encoding="utf-8"))
    except Exception:
        return {}

def save(data):
    json.dump(data, open(PATH, "w", encoding="utf-8"), indent=2)

def _fingerprint(goal):
    gid = str(goal.get("goal_id") or goal.get("id") or "")
    gtype = str(goal.get("goal_type") or "")
    reason = str(goal.get("reason") or "")

    # simple structural signature
    key = f"{gtype}|{gid.split('_')[0]}"

    if "recovery" in reason:
        key += "|recovery"
    if "explore" in reason:
        key += "|explore"
    if "improve" in gid:
        key += "|opt"

    return key

def get_bias(goal):
    data = load()
    key = _fingerprint(goal)
    entry = data.get(key, {})
    return float(entry.get("avg_score", 0.0) or 0.0)

def record(goal, score):
    data = load()
    key = _fingerprint(goal)

    if key not in data:
        data[key] = {
            "runs": 0,
            "total": 0.0,
            "avg_score": 0.0,
            "last_updated": None
        }

    entry = data[key]
    entry["runs"] += 1
    entry["total"] += float(score or 0.0)
    entry["avg_score"] = entry["total"] / entry["runs"]
    entry["last_updated"] = time.time()

    save(data)
    return entry
