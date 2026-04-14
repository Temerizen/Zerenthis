import random

def rebellion_trigger():
    # 20% chance to IGNORE all logic
    return random.random() < 0.2

def full_random_params():
    return {
        "risk_per_trade": random.uniform(0.01, 0.15),
        "take_profit": random.uniform(0.01, 0.06),
        "stop_loss": random.uniform(0.005, 0.05),
        "position_scale": random.uniform(0.5, 2.5)
    }

