import random

def simulate_market_outcome(change):
    # true market movement deviates from observed signal
    real_change = change + random.uniform(-3, 3)

    # occasional full reversal
    if random.random() < 0.2:
        real_change *= -1

    return real_change
