import json, os

META_PATH = "backend/data/meta_intelligence.json"
BAD_IDS = {
    "selected_at",
    "primary_goal",
    "secondary_goals",
    "exploration_thread",
    "ranked_goals",
    "meta",
    "active_goal",
    "history",
    "preferences",
    "status",
}

def load_meta():
    if not os.path.exists(META_PATH):
        return {"preferences": {}, "history": []}
    try:
        with open(META_PATH, "r", encoding="utf-8") as f:
            raw = f.read().strip()
            if not raw:
                return {"preferences": {}, "history": []}
            return json.loads(raw)
    except Exception:
        return {"preferences": {}, "history": []}

def save_meta(data):
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _extract_goal(obj):
    if not isinstance(obj, dict):
        return None

    # direct goal
    gid = obj.get("id")
    if gid and gid not in BAD_IDS:
        return obj

    # nested shapes
    for key in ("active_goal", "primary_goal", "goal"):
        nested = obj.get(key)
        if isinstance(nested, dict):
            gid = nested.get("id")
            if gid and gid not in BAD_IDS:
                return nested

    return None

def update_meta(goal):
    actual = _extract_goal(goal)
    if not actual:
        return load_meta()

    goal_id = actual.get("id", "unknown_goal")
    goal_type = actual.get("goal_type", "unknown")

    if goal_id in BAD_IDS:
        return load_meta()

    data = load_meta()

    prefs = data.setdefault("preferences", {})
    prefs[goal_type] = int(prefs.get(goal_type, 0)) + 1

    history = data.setdefault("history", [])
    history.append({
        "goal_id": goal_id,
        "goal_type": goal_type
    })
    data["history"] = history[-25:]

    save_meta(data)
    return data
