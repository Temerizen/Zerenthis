from typing import List, Dict
from backend.app.engines.market_memory_engine import load_memory

def generate_signals(market_data: List[Dict]):
    memory = load_memory()
    signals = []

    for item in market_data:
        asset = item.get("asset")
        change = float(item.get("change", 0))

        base_conf = abs(change) * 1.5

        mem = memory.get("assets", {}).get(asset, {})
        wins = mem.get("wins", 0)
        losses = mem.get("losses", 0)

        # performance bias
        perf_bias = (wins - losses) * 0.5

        confidence = max(0, min(10, base_conf + perf_bias))

        if change > 2:
            action = "BUY"
        elif change < -2:
            action = "SELL"
        else:
            action = "HOLD"

        signals.append({
            "asset": asset,
            "action": action,
            "confidence": round(confidence, 2),
            "reason": "adaptive_signal",
            "memory_bias": perf_bias
        })

    return signals

