from typing import List, Dict
from backend.app.engines.market_genetics_engine import load_genetics

def _cap_conf(change: float, mult: float, max_conf: float) -> float:
    return min(max_conf, abs(change) * mult)

def momentum_strategy(data, gene):
    signals = []
    threshold = float(gene.get("threshold", 2.0))
    mult = float(gene.get("confidence_mult", 1.5))
    max_conf = float(gene.get("max_conf", 10.0))

    for d in data:
        change = float(d.get("change", 0))
        if change > threshold:
            signals.append({"asset": d["asset"], "action": "BUY", "confidence": _cap_conf(change, mult, max_conf)})
        elif change < -threshold:
            signals.append({"asset": d["asset"], "action": "SELL", "confidence": _cap_conf(change, mult, max_conf)})
    return signals

def mean_reversion_strategy(data, gene):
    signals = []
    threshold = float(gene.get("threshold", 3.0))
    mult = float(gene.get("confidence_mult", 1.2))
    max_conf = float(gene.get("max_conf", 10.0))

    for d in data:
        change = float(d.get("change", 0))
        if change > threshold:
            signals.append({"asset": d["asset"], "action": "SELL", "confidence": _cap_conf(change, mult, max_conf)})
        elif change < -threshold:
            signals.append({"asset": d["asset"], "action": "BUY", "confidence": _cap_conf(change, mult, max_conf)})
    return signals

def breakout_strategy(data, gene):
    signals = []
    threshold = float(gene.get("threshold", 5.0))
    mult = float(gene.get("confidence_mult", 2.0))
    max_conf = float(gene.get("max_conf", 10.0))

    for d in data:
        change = float(d.get("change", 0))
        if abs(change) > threshold:
            signals.append({"asset": d["asset"], "action": "BUY" if change > 0 else "SELL", "confidence": _cap_conf(change, mult, max_conf)})
    return signals

def conservative_strategy(data, gene):
    signals = []
    threshold = float(gene.get("threshold", 4.0))
    mult = float(gene.get("confidence_mult", 1.0))
    max_conf = float(gene.get("max_conf", 6.0))

    for d in data:
        change = float(d.get("change", 0))
        if change >= threshold:
            signals.append({"asset": d["asset"], "action": "BUY", "confidence": _cap_conf(change, mult, max_conf)})
        elif change <= -threshold:
            signals.append({"asset": d["asset"], "action": "SELL", "confidence": _cap_conf(change, mult, max_conf)})
    return signals

STRATEGIES = {
    "momentum": momentum_strategy,
    "mean_reversion": mean_reversion_strategy,
    "breakout": breakout_strategy,
    "conservative": conservative_strategy
}

def run_strategies(data: List[Dict]):
    genetics = load_genetics()
    results = {}

    for name, strat in STRATEGIES.items():
        gene = genetics.get(name, {})
        signals = strat(data, gene)
        wins = 0
        losses = 0
        profit_total = 0.0

        for s in signals:
            asset_row = next((d for d in data if d.get("asset") == s.get("asset")), {})
            change = float(asset_row.get("change", 0))
            action = s.get("action")
            confidence = float(s.get("confidence", 0))

            raw = (abs(change) / 100.0) * (confidence * 0.5)

            if (action == "BUY" and change > 0) or (action == "SELL" and change < 0):
                profit = raw
                wins += 1
            else:
                profit = -raw
                losses += 1

            profit_total += profit

        trades = len(signals)
        results[name] = {
            "trades": trades,
            "wins": wins,
            "losses": losses,
            "profit": round(profit_total, 2),
            "winrate": round((wins / max(trades, 1)) * 100, 2) if trades else 0,
            "gene": gene
        }

    best = max(results.items(), key=lambda x: x[1]["profit"])[0] if results else "conservative"

    return {
        "strategies": results,
        "best_strategy": best,
        "leaderboard": sorted(results.items(), key=lambda x: x[1]["profit"], reverse=True),
        "genetics": genetics
    }

