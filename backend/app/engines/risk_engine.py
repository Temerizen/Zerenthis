def calculate_position_size(balance, risk_per_trade, change):
    max_risk = balance * risk_per_trade

    volatility_factor = min(abs(change) / 10, 1.5)

    position_size = max_risk / (1 + volatility_factor)

    return round(position_size, 2)

