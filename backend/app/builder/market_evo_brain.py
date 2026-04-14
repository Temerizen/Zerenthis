import random

ASSETS = ["BTC", "ETH", "SOL"]
ACTIONS = ["buy", "sell", "skip"]

def random_signal():
    return {
        "asset": random.choice(ASSETS),
        "action": random.choice(ACTIONS)
    }

def propose_variants(k=2, current=None):
    variants = []

    for _ in range(k):
        v = {
            "risk_per_trade": max(0.02, min(0.15, (current or {}).get("risk_per_trade", 0.08) + random.uniform(-0.02, 0.02))),
            "take_profit": max(0.01, min(0.06, (current or {}).get("take_profit", 0.03) + random.uniform(-0.01, 0.01))),
            "stop_loss": max(0.005, min(0.05, (current or {}).get("stop_loss", 0.02) + random.uniform(-0.01, 0.01))),
            "position_scale": max(0.5, min(2.0, (current or {}).get("position_scale", 1.0) + random.uniform(-0.5, 0.5))),
            "signals": [random_signal() for _ in range(3)]
        }
        variants.append(v)

    return variants

