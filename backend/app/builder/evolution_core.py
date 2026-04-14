import random, copy, json, os

FILE = "backend/data/performance_memory.json"

def load():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def mutate(params, strength=0.2):
    new = copy.deepcopy(params)
    for k in ["risk_per_trade","take_profit","stop_loss","position_scale"]:
        if k in new:
            delta = new[k] * strength * (random.random()*2-1)
            new[k] = max(0.001, new[k] + delta)
    return new

def get_diverse_elites():
    mem = load()
    if not mem:
        return []

    unique = {}
    for m in mem:
        key = str({k: round(v,2) for k,v in m["params"].items()})
        if key not in unique or m["score"] > unique[key]["score"]:
            unique[key] = m

    elites = sorted(unique.values(), key=lambda x: x["score"], reverse=True)
    return elites[:5]

def should_break_stagnation():
    mem = load()
    if len(mem) < 10:
        return False

    last = mem[-10:]
    scores = [m["score"] for m in last]

    return max(scores) - min(scores) < 0.5

def generate_next(params):
    elites = get_diverse_elites()

    if should_break_stagnation():
        return random.choice(elites)["params"] if elites else params

    if elites:
        base = random.choice(elites)["params"]
        return mutate(base, 0.15)

    return mutate(params, 0.3)

