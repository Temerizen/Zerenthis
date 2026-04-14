from typing import List, Dict

def momentum_strategy(item: Dict) -> Dict:
    change = float(item.get("change", 0))
    if change >= 5:
        return {"action": "BUY", "reason": "momentum_strong_up"}
    if change <= -5:
        return {"action": "SELL", "reason": "momentum_strong_down"}
    if change >= 2:
        return {"action": "BUY", "reason": "momentum_up"}
    if change <= -2:
        return {"action": "SELL", "reason": "momentum_down"}
    return {"action": "HOLD", "reason": "momentum_no_edge"}

def reversal_strategy(item: Dict) -> Dict:
    change = float(item.get("change", 0))
    if change >= 6:
        return {"action": "SELL", "reason": "reversal_overextended_up"}
    if change <= -6:
        return {"action": "BUY", "reason": "reversal_oversold_down"}
    return {"action": "HOLD", "reason": "reversal_no_edge"}

def conservative_strategy(item: Dict) -> Dict:
    change = float(item.get("change", 0))
    if change >= 4:
        return {"action": "BUY", "reason": "conservative_upside"}
    if change <= -4:
        return {"action": "SELL", "reason": "conservative_downside"}
    return {"action": "HOLD", "reason": "conservative_no_edge"}

STRATEGIES = {
    "momentum": momentum_strategy,
    "reversal": reversal_strategy,
    "conservative": conservative_strategy,
}

def generate_multi_signals(market_data: List[Dict]) -> Dict:
    results = {}

    for strategy_name, strategy_fn in STRATEGIES.items():
        strategy_signals = []
        for item in market_data:
            outcome = strategy_fn(item)
            strategy_signals.append({
                "asset": item.get("asset"),
                "strategy": strategy_name,
                "action": outcome["action"],
                "reason": outcome["reason"],
                "change": round(float(item.get("change", 0)), 2),
                "price": round(float(item.get("price", 0)), 2),
            })
        results[strategy_name] = strategy_signals

    return results

