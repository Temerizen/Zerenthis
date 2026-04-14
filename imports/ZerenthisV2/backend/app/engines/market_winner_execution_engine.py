from backend.app.engines.market_strategy_competition import run_strategies
from backend.app.engines.market_winner_signal_engine import build_signals_for_strategy
from backend.app.engines.market_data_engine import scan_market
from backend.app.engines.market_paper_engine import run_paper_trades
from backend.app.engines.market_score_engine import score_trades
from backend.app.engines.market_portfolio_engine import load_portfolio
from backend.app.engines.market_memory_engine import update_memory

def run_winner_cycle():
    data = scan_market()

    # Step 1: find best strategy
    strat_results = run_strategies(data)
    best = strat_results["best_strategy"]

    # Step 2: generate signals ONLY from winner
    signals = build_signals_for_strategy(best, data)

    # Step 3: execute trades
    trades = run_paper_trades(signals, data)

    # Step 4: score + learn
    score = score_trades(trades)
    memory = update_memory(trades)
    portfolio = load_portfolio()

    return {
        "status": "winner_cycle_complete",
        "best_strategy": best,
        "signals": signals,
        "trades": trades,
        "score": score,
        "memory": memory,
        "portfolio": portfolio
    }
