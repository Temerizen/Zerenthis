import json, os, time, random

STRATEGY_PATH = "backend/data/strategy.json"

def load():
    if not os.path.exists(STRATEGY_PATH):
        return {
            "active_strategy": "default",
            "strategies": {"default": {"score": 0.5, "uses": 0, "mutations": 0}},
            "history": []
        }
    try:
        return json.load(open(STRATEGY_PATH))
    except:
        return {
            "active_strategy": "default",
            "strategies": {"default": {"score": 0.5, "uses": 0, "mutations": 0}},
            "history": []
        }

def save(data):
    with open(STRATEGY_PATH, "w") as f:
        json.dump(data, f, indent=2)

def mutate_name(base):
    return f"{base}_mut_{int(time.time())}_{random.randint(1,999)}"

def run(context):
    data = load()

    score = context.get("score", 0.5)

    current = data["active_strategy"]
    strat = data["strategies"].get(current, {"score": 0.5, "uses": 0, "mutations": 0})

    strat["uses"] += 1
    strat["score"] = (strat["score"] + score) / 2

    action = "none"
    new_strategy = None

    # =========================
    # EVOLUTION LOGIC
    # =========================
    if score < 0.4:
        # mutate
        new_name = mutate_name(current)
        data["strategies"][new_name] = {
            "score": score,
            "uses": 0,
            "mutations": 0
        }
        data["active_strategy"] = new_name
        strat["mutations"] += 1

        action = "mutated"
        new_strategy = new_name

    elif score > 0.75:
        action = "reinforced"

    else:
        action = "stable"

    data["strategies"][current] = strat

    data["history"].append({
        "timestamp": time.time(),
        "strategy": current,
        "score": score,
        "action": action
    })

    save(data)

    return {
        "status": "strategy_updated",
        "active_strategy": data["active_strategy"],
        "action": action,
        "strategy_score": strat["score"]
    }
