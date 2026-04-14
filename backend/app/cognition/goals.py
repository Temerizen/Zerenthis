import json, time, os

GOALS_PATH = "backend/data/goals.json"

def load():
    if not os.path.exists(GOALS_PATH):
        return {"active_goals": [], "history": []}
    try:
        return json.load(open(GOALS_PATH))
    except:
        return {"active_goals": [], "history": []}

def save(data):
    with open(GOALS_PATH, "w") as f:
        json.dump(data, f, indent=2)

def new_goal(goal_type):
    return {
        "id": f"goal_{int(time.time())}",
        "type": goal_type,
        "description": f"Pursue {goal_type}",
        "priority": 0.6,
        "commitment": 0.5,
        "progress": 0.0,
        "status": "active",
        "created_at": time.time(),
        "last_updated": time.time(),
        "cycles_active": 0
    }

def resolve_goal(context):
    if context.get("goal"):
        return context["goal"]
    if context.get("dominant_value"):
        return context["dominant_value"]
    return "exploration"

def run(context):
    data = load()
    goals = data.get("active_goals", [])

    goal_type = resolve_goal(context)

    if not goals:
        g = new_goal(goal_type)
        data["active_goals"] = [g]
    else:
        g = goals[0]

    # ALIGNMENT PENALTY
    if g["type"] != goal_type:
        g["commitment"] -= 0.05

    # UPDATE
    g["cycles_active"] += 1
    g["progress"] += 0.05
    g["last_updated"] = time.time()

    # REINFORCE / DECAY
    if g["type"] == goal_type:
        g["commitment"] += 0.04
    else:
        g["commitment"] -= 0.03

    # CLAMP
    g["commitment"] = max(0, min(1, g["commitment"]))

    # DROP
    if g["commitment"] < 0.2:
        g["status"] = "dropped"
        data["history"].append(g)
        data["active_goals"] = []
        save(data)
        return {"status": "goal_dropped", "active_goal": None}

    # COMPLETE
    if g["progress"] >= 1.0:
        g["status"] = "completed"
        data["history"].append(g)
        data["active_goals"] = []
        save(data)
        return {"status": "goal_completed", "active_goal": None}

    data["active_goals"] = [g]
    save(data)

    return {"status": "goal_updated", "active_goal": g}
