import json
import os

PERF_FILE = "backend/data/strategy_performance.json"

DEFAULT = {
    "momentum": {"wins": 0, "losses": 0, "score": 0.0},
    "mean_reversion": {"wins": 0, "losses": 0, "score": 0.0},
    "breakout": {"wins": 0, "losses": 0, "score": 0.0},
    "conservative": {"wins": 0, "losses": 0, "score": 0.0}
}

def load_perf():
    if not os.path.exists(PERF_FILE):
        return DEFAULT.copy()
    with open(PERF_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    for k, v in DEFAULT.items():
        if k not in data:
            data[k] = v.copy()
    return data

def save_perf(data):
    with open(PERF_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def update_strategy_result(strategy_name, pnl):
    perf = load_perf()
    if strategy_name not in perf:
        perf[strategy_name] = {"wins": 0, "losses": 0, "score": 0.0}

    if pnl > 0:
        perf[strategy_name]["wins"] += 1
        perf[strategy_name]["score"] += abs(pnl)
    elif pnl < 0:
        perf[strategy_name]["losses"] += 1
        perf[strategy_name]["score"] -= abs(pnl)

    save_perf(perf)
    return perf[strategy_name]

def best_strategy():
    perf = load_perf()

    # Convert to weighted scores
    weighted = []
    for name, data in perf.items():
        score = float(data.get("score", 0.0))

        # penalize negative strategies hard
        if score < 0:
            score *= 2

        weighted.append((name, score))

    # sort by adjusted score
    weighted.sort(key=lambda x: x[1], reverse=True)

    top_name, top_score = weighted[0]

    # 🛑 if ALL strategies are bad → go conservative
    if top_score <= 0:
        return "conservative"

    return top_name

def confidence_multiplier(strategy_name):
    perf = load_perf()
    row = perf.get(strategy_name, {"score": 0.0})
    score = float(row.get("score", 0.0))
    if score > 0.02:
        return 1.25
    if score > 0.005:
        return 1.10
    if score < -0.02:
        return 0.80
    if score < -0.005:
        return 0.90
    return 1.0

