def build_signal(asset, strategy_name, dna, bias):
    change = asset.get("change", 0)
    price = asset.get("price", 0)

    aggression = dna.get(strategy_name, {}).get("aggression", 0.5) * bias
    threshold = dna.get(strategy_name, {}).get("threshold", 3.0)

    direction = "HOLD"
    confidence = abs(change)

    # =========================
    # STRATEGY LOGIC (REAL RULES)
    # =========================
    if strategy_name == "momentum":
        if change > threshold:
            direction = "BUY"
        elif change < -threshold:
            direction = "SELL"

    elif strategy_name == "mean_reversion":
        if change < -threshold:
            direction = "BUY"
        elif change > threshold:
            direction = "SELL"

    elif strategy_name == "breakout":
        if abs(change) > threshold * 1.2:
            direction = "BUY" if change > 0 else "SELL"

    elif strategy_name == "conservative":
        if abs(change) < threshold * 0.7:
            direction = "BUY" if change > 0 else "SELL"

    # =========================
    # SIGNAL STRENGTH
    # =========================
    strength = min(max((confidence / (threshold+0.1)) * aggression, 0), 1)

    return {
        "asset": asset["asset"],
        "action": direction,
        "confidence": round(strength, 3),
        "raw_change": change,
        "price": price
    }

