import json, os, random

DNA_PATH = "backend/data/strategy_dna.json"

BASE_DNA = {
    "momentum": {"aggression": 0.7, "threshold": 3.0},
    "mean_reversion": {"aggression": 0.6, "threshold": 3.0},
    "breakout": {"aggression": 0.8, "threshold": 2.5},
    "conservative": {"aggression": 0.5, "threshold": 2.0}
}

def load_dna():
    if os.path.exists(DNA_PATH):
        with open(DNA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return BASE_DNA.copy()

def save_dna(dna):
    os.makedirs(os.path.dirname(DNA_PATH), exist_ok=True)
    with open(DNA_PATH, "w", encoding="utf-8") as f:
        json.dump(dna, f, indent=2)

def mutate(value, rate=0.15):
    change = random.uniform(-rate, rate)
    return round(max(0.1, min(1.5, value + change)), 3)

def evolve(dna, leaderboard):
    if not leaderboard:
        return dna

    # sort by performance
    ranked = sorted(leaderboard, key=lambda x: x["total_profit"], reverse=True)
    best = ranked[0]["name"]
    worst = ranked[-1]["name"]

    # mutate worst strategy towards best
    for key in dna.get(worst, {}):
        dna[worst][key] = mutate(dna[best][key])

    # slight mutation to all others
    for name in dna:
        if name != best:
            for key in dna[name]:
                dna[name][key] = mutate(dna[name][key], 0.05)

    return dna
