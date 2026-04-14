from typing import Dict, List
from backend.app.engines.market_paper_engine import run_paper_trades
from backend.app.engines.market_score_engine import score_trades

def evaluate_strategies(multi_signals: Dict[str, List[Dict]], market_data: List[Dict]) -> Dict:
    results = {}

    for strategy_name, signals in multi_signals.items():
        trades = run_paper_trades(signals, market_data, persist=False)
        score = score_trades(trades)
        results[strategy_name] = {
            "signals": signals,
            "trades": trades,
            "score": score,
        }

    best_name = max(
        results.keys(),
        key=lambda name: (
            float(results[name]["score"].get("total_profit", 0)),
            float(results[name]["score"].get("wins", 0))
        )
    )

    return {
        "best_strategy": best_name,
        "results": results
    }

