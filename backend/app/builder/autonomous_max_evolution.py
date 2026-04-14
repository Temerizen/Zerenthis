import random
import json
import os
import time

from backend.app.builder.performance_memory import record_run, get_best

PARAMS_FILE = "backend/data/market_params.json"

def load():
    if os.path.exists(PARAMS_FILE):
        with open(PARAMS_FILE, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    else:
        data = {}

    data.setdefault("balance", 1000)
    data.setdefault("risk_per_trade", 0.05)
    data.setdefault("take_profit", 0.02)
    data.setdefault("stop_loss", 0.01)
    data.setdefault("position_scale", 1.0)
    return data

def save(params):
    os.makedirs("backend/data", exist_ok=True)
    with open(PARAMS_FILE, "w", encoding="utf-8") as f:
        json.dump(params, f, indent=2)

def mutate(params):
    return {
        "balance": params.get("balance", 1000),
        "risk_per_trade": max(0.01, min(0.15, params.get("risk_per_trade", 0.05) + random.uniform(-0.01, 0.01))),
        "take_profit": max(0.005, min(0.06, params.get("take_profit", 0.02) + random.uniform(-0.005, 0.005))),
        "stop_loss": max(0.005, min(0.05, params.get("stop_loss", 0.01) + random.uniform(-0.005, 0.005))),
        "position_scale": max(0.5, min(2.5, params.get("position_scale", 1.0) + random.uniform(-0.2, 0.2)))
    }

def rebellion():
    return {
        "balance": 1000,
        "risk_per_trade": random.uniform(0.01, 0.15),
        "take_profit": random.uniform(0.01, 0.06),
        "stop_loss": random.uniform(0.005, 0.05),
        "position_scale": random.uniform(0.5, 2.5)
    }

def simulate(params):
    trades = random.randint(1, 3)
    exposure = params["risk_per_trade"] * params["balance"] * trades
    pnl = exposure * random.uniform(-0.05, 0.08)
    return {
        "status": "simulated",
        "trades": trades,
        "exposure": exposure,
        "pnl": pnl
    }

def score(sim):
    pnl = sim["pnl"]
    exposure = sim["exposure"]
    if exposure == 0:
        return -1.0
    efficiency = pnl / exposure
    consistency_penalty = 0 if pnl > 0 else abs(pnl) * 0.5
    return (efficiency * 100) - consistency_penalty

def run_once():
    params = load()

    if random.random() < 0.2:
        challenger = rebellion()
    else:
        challenger = mutate(params)

    sim = simulate(challenger)
    new_score = score(sim)

    current_sim = simulate(params)
    current_score = score(current_sim)

    if new_score > current_score:
        final = challenger
        final_score = new_score
        final_sim = sim
        decision = "challenger_won"
        save(final)
    else:
        final = params
        final_score = current_score
        final_sim = current_sim
        decision = "rejected_regression"

    best = get_best()
    best_params = best.get("params") if best else None
    best_score = best.get("score", float("-inf")) if best else float("-inf")

    if best_params and best_score > final_score:
        if random.random() < 0.7:
            final = best_params
            final_score = best_score
            final_sim = {"status": "memory_restore"}
            decision = "best_memory_restored"
            save(final)
        else:
            decision = "exploration_override"

    record_run(final, final_score)

    return {
        "status": "applied",
        "decision": decision,
        "score": final_score,
        "sim": final_sim,
        "params": final
    }

def run_loop(iterations=10, delay=1):
    history = []
    for _ in range(iterations):
        result = run_once()
        history.append(result)
        time.sleep(delay)
    return {
        "status": "loop_complete",
        "iterations": iterations,
        "history": history
    }

