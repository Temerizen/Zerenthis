import json, os, time, random

STRATEGY_PATH = "backend/data/strategy.json"

def load():
    if not os.path.exists(STRATEGY_PATH):
        return {"current_strategy": "default", "history": []}
    try:
        return json.load(open(STRATEGY_PATH))
    except:
        return {"current_strategy": "default", "history": []}

def save(data):
    with open(STRATEGY_PATH, "w") as f:
        json.dump(data, f, indent=2)

def mutate(current):
    variants = [
        "explore_more",
        "optimize_focus",
        "reduce_risk",
        "increase_efficiency"
    ]
    return random.choice(variants)

def run(context):
    data = load()

    score = context.get("score", 0.5)
    current = data.get("current_strategy", "default")

    decision = None

    if score < 0.4:
        new_strategy = mutate(current)
        decision = "mutated"
        data["history"].append({
            "from": current,
            "to": new_strategy,
            "timestamp": time.time()
        })
        data["current_strategy"] = new_strategy

    else:
        new_strategy = current
        decision = "kept"

    save(data)

    return {
        "status": "strategy_updated",
        "strategy": new_strategy,
        "decision": decision
    }
