import random

def simulate(portfolio, params):
    balance = float(portfolio.get("balance", 1000))

    risk = float(params.get("risk_per_trade", 0.08))
    tp = float(params.get("take_profit", 0.03))
    sl = float(params.get("stop_loss", 0.02))
    scale = float(params.get("position_scale", 1.0))

    signals = params.get("signals")
    if not signals:
        signals = [
            {"asset": "BTC", "action": "buy"},
            {"asset": "ETH", "action": "buy"},
            {"asset": "SOL", "action": "buy"}
        ]

    pnl = 0.0
    trades = 0

    for s in signals:
        action = s.get("action", "skip")

        if action == "skip":
            continue

        entry = 100.0
        size = (balance * risk * scale) / entry

        price = entry

        for _ in range(10):
            move = random.uniform(-0.02, 0.02)
            price *= (1 + move)

            change = (price - entry) / entry

            if action == "sell":
                change = -change

            if change >= tp:
                pnl += tp * size * entry
                trades += 1
                break

            if change <= -sl:
                pnl -= sl * size * entry
                trades += 1
                break

    exposure = balance * risk * scale * max(1, trades)

    return {
        "status": "simulated",
        "pnl": pnl,
        "trades": trades,
        "exposure": exposure
    }
