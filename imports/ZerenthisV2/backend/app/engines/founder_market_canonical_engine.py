import time
import importlib
import random
import json
import os
from backend.app.engines.strategy_performance_engine import best_strategy, confidence_multiplier, update_strategy_result

def _resolve(module_name, candidate_names, required=True):
    mod = importlib.import_module(module_name)
    for name in candidate_names:
        fn = getattr(mod, name, None)
        if callable(fn):
            return fn
    if required:
        raise ImportError(f"No callable found in {module_name}. Tried: {candidate_names}")
    return None

def _safe_dict(value, default=None):
    if default is None:
        default = {}
    return value if isinstance(value, dict) else default

def _safe_list(value):
    return value if isinstance(value, list) else []

def _load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        except:
            return default.copy() if isinstance(default, dict) else default
    return default.copy() if isinstance(default, dict) else default

def _load_portfolio_engine():
    return importlib.import_module("backend.app.engines.market_portfolio_engine")

def _fallback_strategy_results(data):
    winner = best_strategy()
    strategies = {
        "momentum": {"trades": 0, "wins": 0, "losses": 0, "profit": 0.0, "winrate": 0.0},
        "mean_reversion": {"trades": 0, "wins": 0, "losses": 0, "profit": 0.0, "winrate": 0.0},
        "breakout": {"trades": 0, "wins": 0, "losses": 0, "profit": 0.0, "winrate": 0.0},
        "conservative": {"trades": 0, "wins": 0, "losses": 0, "profit": 0.0, "winrate": 0.0}
    }
    return {
        "best_strategy": winner,
        "strategies": strategies,
        "signals": []
    }

def _hybrid_action(change: float) -> str:
    if abs(change) > 3.0:
        return "SELL" if change > 0 else "BUY"
    return "BUY" if change > 0 else "SELL"

def _winner_only_signals(strategy_results, data):
    winner = strategy_results.get("best_strategy", "conservative")
    mult = confidence_multiplier(winner)
    out = []

    for item in data:
        if not isinstance(item, dict):
            continue

        asset = item.get("asset")
        price = float(item.get("price", 0) or 0)
        change = float(item.get("change", 0) or 0)

        if not asset or price <= 0:
            continue

        action = _hybrid_action(change)

        if winner == "breakout":
            if abs(change) >= 2.0:
                out.append({
                    "asset": asset,
                    "action": action,
                    "price": price,
                    "confidence": round(max(1.0, abs(change)) * mult, 4),
                    "reason": "winner_breakout",
                    "strategy": "breakout"
                })

        elif winner == "conservative":
            if abs(change) >= 1.5:
                out.append({
                    "asset": asset,
                    "action": action,
                    "price": price,
                    "confidence": round(max(1.0, abs(change)) * mult, 4),
                    "reason": "winner_conservative",
                    "strategy": "conservative"
                })

        elif winner == "momentum":
            if abs(change) >= 2.0:
                out.append({
                    "asset": asset,
                    "action": action,
                    "price": price,
                    "confidence": round(max(1.0, abs(change)) * mult, 4),
                    "reason": "winner_momentum",
                    "strategy": "momentum"
                })

        elif winner == "mean_reversion":
            if abs(change) >= 2.5:
                out.append({
                    "asset": asset,
                    "action": "SELL" if change > 0 else "BUY",
                    "price": price,
                    "confidence": round(max(1.0, abs(change)) * mult, 4),
                    "reason": "winner_mean_reversion",
                    "strategy": "mean_reversion"
                })

    out = sorted(out, key=lambda x: float(x.get("confidence", 0) or 0), reverse=True)[:1]
    return out

def _quality_gate(signals, chosen_strategy):
    perf = _load_json("backend/data/strategy_performance.json", {})
    streak = _load_json("backend/data/streak_state.json", {"win_streak": 0, "loss_streak": 0})

    strat_score = float(perf.get(chosen_strategy, {}).get("score", 0.0))
    loss_streak = int(streak.get("loss_streak", 0))

    gated = []
    for s in signals:
        confidence = float(s.get("confidence", 0) or 0)

        # Hard filters
        if strat_score < 0.005:
            continue
        if confidence < 1.75:
            continue
        if loss_streak >= 2:
            continue

        gated.append(s)

    return gated

def run_full_cycle():
    get_data = _resolve(
        "backend.app.engines.market_data_engine",
        ["get_market_data", "fetch_market_data", "scan_market", "run_market_scan", "get_data"]
    )
    run_paper_trades = _resolve(
        "backend.app.engines.market_paper_engine",
        ["run_paper_trades"]
    )
    score_trades = _resolve(
        "backend.app.engines.market_score_engine",
        ["score_trades"]
    )
    load_portfolio = _resolve(
        "backend.app.engines.market_portfolio_engine",
        ["load_portfolio"]
    )
    evolve_strategies = _resolve(
        "backend.app.engines.market_adaptive_engine",
        ["evolve_strategies"]
    )
    strategy_fn = _resolve(
        "backend.app.engines.market_strategy_engine",
        ["run_strategies", "generate_strategy_signals", "build_signals", "run_strategy_engine"],
        required=False
    )

    data = get_data()
    if isinstance(data, dict):
        data = data.get("scan", data.get("data", data))
    data = _safe_list(data)

    if strategy_fn:
        strategy_results = strategy_fn(data)
        strategy_results = _safe_dict(strategy_results, {
            "best_strategy": best_strategy(),
            "strategies": {},
            "signals": []
        })
    else:
        strategy_results = _fallback_strategy_results(data)

    if not strategy_results.get("best_strategy"):
        strategy_results["best_strategy"] = best_strategy()

    chosen_strategy = strategy_results.get("best_strategy", "conservative")
    signals = _winner_only_signals(strategy_results, data)
    signals = _quality_gate(signals, chosen_strategy)

    trades = run_paper_trades(data, signals)
    trades = _safe_list(trades)

    loop_pnl = round(sum(float(t.get("pnl", 0) or 0) for t in trades if isinstance(t, dict)), 4)
    update_strategy_result(chosen_strategy, loop_pnl)

    score = score_trades(trades)
    score = _safe_dict(score, {
        "total_profit": 0.0,
        "wins": 0,
        "losses": 0,
        "trades": len(trades),
        "ending_balance": 50.0,
        "pnl_percent": 0.0
    })

    portfolio = load_portfolio()
    portfolio = _safe_dict(portfolio, {"balance": 50.0})

    genetics = evolve_strategies(strategy_results)
    genetics = _safe_dict(genetics, {})

    return {
        "status": "full_cycle_complete",
        "best_strategy": chosen_strategy,
        "strategy_results": strategy_results,
        "scan": data,
        "signals": signals,
        "trades": trades,
        "score": score,
        "portfolio": portfolio,
        "genetics": genetics,
        "updated_at": int(time.time())
    }

def run_winner_cycle():
    return run_full_cycle()

def run_strategy_cycle():
    return run_full_cycle()

def reset_founder_portfolio(starting_balance=50.0, risk_per_trade=0.1):
    portfolio_engine = _load_portfolio_engine()
    reset_fn = getattr(portfolio_engine, "reset_portfolio", None)
    if not callable(reset_fn):
        raise ImportError("reset_portfolio not found in market_portfolio_engine")
    return reset_fn(starting_balance=starting_balance, risk_per_trade=risk_per_trade)
