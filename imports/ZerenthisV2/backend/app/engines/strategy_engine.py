import json, os
from datetime import datetime
from backend.app.engines.mutation_engine import load_dna, save_dna, evolve
from backend.app.engines.memory_engine import record_cycle, detect_patterns, get_bias
from backend.app.engines.real_signal_engine import build_signal
from backend.app.engines.real_trade_engine import execute_trade

DATA_PATH = "backend/data/strategy_leaderboard.json"

def load_leaderboard():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_leaderboard(data):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def run_strategy(name, market_data, dna, bias, portfolio):
    trades = []
    wins = 0
    losses = 0
    total_profit = 0

    for asset in market_data:
        signal = build_signal(asset, name, dna, bias)
        trade = execute_trade(signal, portfolio)

        if trade:
            


trades.append(trade)
            profit = trade["profit"]
            total_profit += profit

            if profit > 0:
                wins += 1
            else:
                losses += 1

    total_profit = round(total_profit, 2)
    total_trades = len(trades)
    winrate = round((wins / total_trades) * 100, 2) if total_trades else 0

    return {
        "name": name,
        "trades": total_trades,
        "wins": wins,
        "losses": losses,
        "profit": total_profit,
        "winrate": winrate,
        "executed_trades": trades
    }

def run_strategies(market_data, portfolio):
    dna = load_dna()

    pattern_data = detect_patterns()
    pattern = pattern_data["pattern"]
    bias = get_bias(pattern)

    strategy_names = list(dna.keys())

    results = []

    # Each strategy runs on CLONED portfolio (fair competition)
    for name in strategy_names:
        local_portfolio = portfolio.copy()
        result = run_strategy(name, market_data, dna, bias, local_portfolio)
        results.append(result)

    ranked = sorted(results, key=lambda x: x["profit"], reverse=True)
    best = ranked[0]

    # Update real portfolio ONLY with best strategy trades
    for t in best["executed_trades"]:
        portfolio["balance"] = t["balance_after"]

    board = load_leaderboard()

    for r in results:
        name = r["name"]
        if name not in board:
            board[name] = {"total_profit": 0, "runs": 0}

        board[name]["total_profit"] += r["profit"]
        board[name]["runs"] += 1

    save_leaderboard(board)

    global_rank = sorted(
        [{"name": k, "total_profit": v["total_profit"]} for k,v in board.items()],
        key=lambda x: x["total_profit"],
        reverse=True
    )

    dna = evolve(dna, global_rank)
    save_dna(dna)

    record_cycle(market_data, results, best)

    portfolio["active_strategy"] = best["name"]
    portfolio["market_pattern"] = pattern

    return {
        "strategies": results,
        "best_strategy": best,
        "leaderboard": global_rank,
        "market_pattern": pattern,
        "portfolio": portfolio,
        "timestamp": datetime.utcnow().isoformat()
    }


