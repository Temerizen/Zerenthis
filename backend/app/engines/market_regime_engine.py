def detect_market_regime(change):
    if change > 3:
        return "bull"
    elif change < -3:
        return "bear"
    elif abs(change) < 1.5:
        return "sideways"
    else:
        return "volatile"

