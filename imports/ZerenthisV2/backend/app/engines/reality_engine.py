import random

def apply_execution_reality(position_size, change_percent):
    fee_rate = 0.001
    slippage_rate = 0.0015

    raw_profit = position_size * (change_percent / 100)

    fees = position_size * fee_rate
    slippage = position_size * slippage_rate

    profit = raw_profit - fees - slippage
    return round(profit, 4)
