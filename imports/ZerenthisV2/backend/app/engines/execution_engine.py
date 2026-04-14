def calculate_trade_profit(action, position_size, real_change):
    # BUY: profit if price goes up
    if action == "BUY":
        pnl = real_change * position_size
    else:
        # SELL: profit if price goes down
        pnl = (-real_change) * position_size

    return round(pnl, 4)
