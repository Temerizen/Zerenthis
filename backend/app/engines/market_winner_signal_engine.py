from typing import List, Dict
from backend.app.engines.market_genetics_engine import load_genetics

def _cap_conf(change: float, mult: float, max_conf: float) -> float:
    return min(max_conf, abs(change) * mult)

def build_signals_for_strategy(strategy_name: str, data: List[Dict]):
    genetics = load_genetics()
    gene = genetics.get(strategy_name, {})
    threshold = float(gene.get("threshold", 2.0))
    mult = float(gene.get("confidence_mult", 1.5))
    max_conf = float(gene.get("max_conf", 10.0))

    signals = []

    for d in data:
        change = float(d.get("change", 0))

        if strategy_name == "momentum":
            if change > threshold:
                signals.append({"asset": d["asset"], "action": "BUY", "confidence": _cap_conf(change, mult, max_conf), "reason": "momentum_up"})
            elif change < -threshold:
                signals.append({"asset": d["asset"], "action": "SELL", "confidence": _cap_conf(change, mult, max_conf), "reason": "momentum_down"})

        elif strategy_name == "mean_reversion":
            if change > threshold:
                signals.append({"asset": d["asset"], "action": "SELL", "confidence": _cap_conf(change, mult, max_conf), "reason": "revert_from_spike"})
            elif change < -threshold:
                signals.append({"asset": d["asset"], "action": "BUY", "confidence": _cap_conf(change, mult, max_conf), "reason": "revert_from_dump"})

        elif strategy_name == "breakout":
            if abs(change) > threshold:
                signals.append({"asset": d["asset"], "action": "BUY" if change > 0 else "SELL", "confidence": _cap_conf(change, mult, max_conf), "reason": "breakout_extension"})

        else:
            if change >= threshold:
                signals.append({"asset": d["asset"], "action": "BUY", "confidence": _cap_conf(change, mult, max_conf), "reason": "conservative_up"})
            elif change <= -threshold:
                signals.append({"asset": d["asset"], "action": "SELL", "confidence": _cap_conf(change, mult, max_conf), "reason": "conservative_down"})

    return signals

