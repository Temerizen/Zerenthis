import json, os

FILE = "backend/data/elite_memory.json"
MAX_ELITES = 10

def load_elites():
    if not os.path.exists(FILE):
        return []
    return json.load(open(FILE, "r"))

def save_elites(elites):
    os.makedirs(os.path.dirname(FILE), exist_ok=True)
    json.dump(elites, open(FILE, "w"), indent=2)

def update_elites(params, score):
    elites = load_elites()

    elites.append({
        "params": params,
        "score": score
    })

    # sort best ? worst
    elites = sorted(elites, key=lambda x: x["score"], reverse=True)

    # keep top N
    elites = elites[:MAX_ELITES]

    save_elites(elites)

def get_random_elite():
    elites = load_elites()
    if not elites:
        return None
    import random
    return random.choice(elites)["params"]

def get_best_elite():
    elites = load_elites()
    if not elites:
        return None
    return elites[0]["params"]

def crossover(p1, p2):
    import random
    child = {}
    for k in p1:
        if k in p2 and isinstance(p1[k], (int, float)):
            child[k] = (p1[k] + p2[k]) / 2 if random.random() < 0.5 else p1[k]
        else:
            child[k] = p1[k]
    return child
