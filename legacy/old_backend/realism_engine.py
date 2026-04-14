import json, os, random

DATA_DIR = os.path.join("backend", "data")
CONFIG_FILE = os.path.join(DATA_DIR, "realism_config.json")

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def ensure_dict(value):
    if isinstance(value, dict):
        return value
    if isinstance(value, list):
        for item in reversed(value):
            if isinstance(item, dict):
                return item
    return {}

def apply_realism(pnl, regime):
    cfg = load_json(CONFIG_FILE, {})

    regime = ensure_dict(regime)  # 🔥 FIX

    fee = cfg.get("fee_rate", 0.001)
    slippage = cfg.get("slippage_base", 0.0015)
    latency = cfg.get("latency_penalty", 0.0005)

    vol_mult = 1.0
    if "HIGH_VOLATILITY" in regime.get("regime", ""):
        vol_mult = cfg.get("volatility_slippage_multiplier", 2.0)

    slippage_effect = slippage * vol_mult * random.uniform(0.8, 1.2)

    total_cost = fee + latency + slippage_effect

    adjusted_pnl = pnl - total_cost

    return {
        "raw_pnl": pnl,
        "adjusted_pnl": adjusted_pnl,
        "costs": {
            "fee": fee,
            "latency": latency,
            "slippage": slippage_effect,
            "total_cost": total_cost
        }
    }
