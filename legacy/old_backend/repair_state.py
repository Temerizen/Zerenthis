from pathlib import Path
from backend.app.engines.state_guard import (
    safe_load_json, safe_save_json,
    normalize_portfolio, normalize_strategy_board,
    normalize_memory, normalize_genetics,
    normalize_performance, normalize_trade_history,
    normalize_market_state
)

targets = {
    Path("backend/data/market/portfolio.json"): normalize_portfolio,
    Path("backend/data/market/strategy_leaderboard.json"): normalize_strategy_board,
    Path("backend/data/market/strategy_memory.json"): normalize_memory,
    Path("backend/data/market/strategy_genetics.json"): normalize_genetics,
    Path("backend/data/market/state.json"): normalize_market_state,
    Path("backend/data/performance.json"): normalize_performance,
    Path("backend/data/trades_history.json"): normalize_trade_history,
}

for path, normalizer in targets.items():
    data = safe_load_json(path, {})
    try:
        fixed = normalizer(data)
    except Exception:
        fixed = normalizer({})
    safe_save_json(path, fixed)

print("STATE REPAIR COMPLETE")
