import json, os, time

STRATEGY_PATH = "backend/data/strategy.json"

def load():
    if not os.path.exists(STRATEGY_PATH):
        return {
            "active_strategy": "default",
            "strategies": {"default": {"score": 0.5, "uses": 0, "mutations": 0}},
            "history": [],
            "leaderboard": []
        }
    try:
        return json.load(open(STRATEGY_PATH))
    except:
        return {
            "active_strategy": "default",
            "strategies": {"default": {"score": 0.5, "uses": 0, "mutations": 0}},
            "history": [],
            "leaderboard": []
        }

def save(data):
    with open(STRATEGY_PATH, "w") as f:
        json.dump(data, f, indent=2)

def run(context):
    data = load()
    score = context.get("score", 0.5)

    strategies = data["strategies"]
    current = data["active_strategy"]

    # =========================
    # UPDATE CURRENT STRATEGY
    # =========================
    strat = strategies.get(current, {"score": 0.5, "uses": 0, "mutations": 0})
    strat["uses"] += 1
    strat["score"] = (strat["score"] + score) / 2
    strategies[current] = strat

    # =========================
    # BUILD LEADERBOARD
    # =========================
    leaderboard = sorted(
        [(name, s["score"]) for name, s in strategies.items()],
        key=lambda x: x[1],
        reverse=True
    )

    data["leaderboard"] = leaderboard

    # =========================
    # SELECT BEST STRATEGY
    # =========================
    best_strategy = leaderboard[0][0] if leaderboard else current

    switched = False
    if best_strategy != current:
        data["active_strategy"] = best_strategy
        switched = True

    # =========================
    # RECORD HISTORY
    # =========================
    data["history"].append({
        "timestamp": time.time(),
        "active": data["active_strategy"],
        "score": score,
        "switched": switched
    })

    save(data)

    return {
        "status": "competition_evaluated",
        "active_strategy": data["active_strategy"],
        "leaderboard": leaderboard,
        "switched": switched
    }
