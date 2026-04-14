import json, os

FILE = "backend/data/performance_memory.json"

def load():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def get_last_scores(n=10):
    mem = load()
    return [m["score"] for m in mem[-n:]]

def improvement_pressure():
    scores = get_last_scores()

    if len(scores) < 5:
        return 1.0

    trend = max(scores) - min(scores)

    if trend < 0.5:
        return 2.5  # STAGNANT → AGGRESSIVE
    elif trend < 1.5:
        return 1.5  # SLOW → MODERATE
    else:
        return 0.8  # GOOD → STABLE

def adaptive_mutation(params):
    import random, copy
    pressure = improvement_pressure()

    new = copy.deepcopy(params)

    for k in ["risk_per_trade","take_profit","stop_loss","position_scale"]:
        if k in new:
            strength = 0.1 * pressure
            delta = new[k] * strength * (random.random()*2-1)
            new[k] = max(0.001, new[k] + delta)

    return new
