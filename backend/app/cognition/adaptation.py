import json, os, time

ADAPT_PATH = "backend/data/adaptation.json"

def load():
    if not os.path.exists(ADAPT_PATH):
        return {"last_adjustment": None, "history": []}
    try:
        return json.load(open(ADAPT_PATH))
    except:
        return {"last_adjustment": None, "history": []}

def save(data):
    with open(ADAPT_PATH, "w") as f:
        json.dump(data, f, indent=2)

def run(context):
    data = load()

    score = context.get("score", 0.5)
    goal = context.get("goal")

    adjustment = {
        "timestamp": time.time(),
        "score": score,
        "action": None,
        "intensity": 0.0
    }

    # =========================
    # ADAPTATION LOGIC
    # =========================
    if score > 0.7:
        adjustment["action"] = "reinforce"
        adjustment["intensity"] = score

    elif score < 0.4:
        adjustment["action"] = "destabilize"
        adjustment["intensity"] = 1 - score

    else:
        adjustment["action"] = "neutral_adjust"
        adjustment["intensity"] = 0.5

    data["last_adjustment"] = adjustment
    data["history"].append(adjustment)

    save(data)

    return {
        "status": "adaptation_applied",
        "adjustment": adjustment
    }
