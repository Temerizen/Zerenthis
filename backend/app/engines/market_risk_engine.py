def apply_risk_controls(signal, portfolio):
    confidence = float(signal.get("confidence", 0))
    action = signal.get("action")

    # ÃƒÂ°Ã…Â¸Ã‚Â§Ã…Â  CONFIDENCE CAP
    confidence = min(confidence, 8.0)

    # ÃƒÂ°Ã…Â¸Ã¢â‚¬Å“Ã¢â‚¬Â° DRAW DOWN PROTECTION
    equity_curve = portfolio.get("equity_curve", [50])
    if len(equity_curve) >= 2:
        if equity_curve[-1] < equity_curve[-2]:
            # Losing ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ reduce aggression
            confidence *= 0.7

    # ÃƒÂ°Ã…Â¸Ã¢â‚¬ÂÃ‚Â¥ WIN STREAK BOOST
    last_trades = portfolio.get("last_run_trades", [])
    wins = sum(1 for t in last_trades if t.get("profit", 0) > 0)

    if wins >= 3:
        confidence *= 1.1  # slight boost

    return round(confidence, 2)


def simulate_stop_loss(position_size, change, action):
    # ÃƒÂ°Ã…Â¸Ã¢â‚¬ÂºÃ¢â‚¬Ëœ HARD STOP LOSS (2%)
    stop_threshold = 0.02

    if action == "BUY" and change < 0:
        loss = min(abs(change) / 100, stop_threshold)
        return -position_size * loss

    if action == "SELL" and change > 0:
        loss = min(abs(change) / 100, stop_threshold)
        return -position_size * loss

    return None

