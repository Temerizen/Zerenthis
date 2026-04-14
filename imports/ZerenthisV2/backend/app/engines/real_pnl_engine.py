def calculate_real_pnl(action, entry_price, change_percent, position_size):
    # convert % change to price movement
    move = change_percent / 100.0

    if action == "BUY":
        pnl = position_size * move
    else:
        pnl = position_size * (-move)

    return round(pnl, 4)
