import json, time, os, random

REALITY_PATH = "backend/data/reality.json"

def load():
    if not os.path.exists(REALITY_PATH):
        return {"history": [], "last_outcome": None}
    try:
        return json.load(open(REALITY_PATH))
    except:
        return {"history": [], "last_outcome": None}

def save(data):
    with open(REALITY_PATH, "w") as f:
        json.dump(data, f, indent=2)

def evaluate_outcome(context):
    # simulate outcome for now (later replaced with real signals)
    base = random.uniform(0.4, 0.8)

    if context.get("mission_progress", 0) > 0:
        base += 0.1

    return min(1.0, base)

def run(context):
    data = load()

    score = evaluate_outcome(context)

    outcome = {
        "timestamp": time.time(),
        "score": score,
        "mission_id": context.get("mission_id"),
        "goal_type": context.get("goal_type")
    }

    data["last_outcome"] = outcome
    data["history"].append(outcome)

    save(data)

    return {
        "status": "outcome_recorded",
        "score": score,
        "outcome": outcome
    }
