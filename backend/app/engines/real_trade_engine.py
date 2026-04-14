def execute_trade(signal, portfolio):
    if signal["action"] == "HOLD":
        return None

    balance = portfolio.get("balance", 1000)
    risk = portfolio.get("risk_per_trade", 0.05)

    position_size = round(balance * risk * signal["confidence"], 2)

    # Profit model based on direction correctness
    change = signal["raw_change"]

    if (signal["action"] == "BUY" and change > 0) or (signal["action"] == "SELL" and change < 0):
        profit = position_size * (abs(change) / 100)
    else:
        profit = -position_size * (abs(change) / 120)

    profit = round(profit, 2)

    portfolio["balance"] = round(balance + profit, 2)

    return {
        "asset": signal["asset"],
        "action": signal["action"],
        "position_size": position_size,
        "profit": profit,
        "balance_after": portfolio["balance"]
    }

