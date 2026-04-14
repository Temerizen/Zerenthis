def is_trade_valid(strategy, regime):
    if regime == "bull" and strategy == "momentum":
        return True
    if regime == "bear" and strategy == "momentum":
        return True
    if regime == "sideways" and strategy == "mean_reversion":
        return True
    if regime == "volatile" and strategy == "conservative":
        return True
    return False
