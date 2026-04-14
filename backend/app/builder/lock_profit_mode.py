import json, os

ACCOUNT_FILE = "backend/data/paper_account.json"
PARAMS_FILE = "backend/data/market_params.json"

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def apply_lock_profit_mode():
    account = load_json(ACCOUNT_FILE, {
        "balance": 1000.0,
        "wins": 0,
        "losses": 0,
        "trades": 0,
        "last_pnl": 0.0
    })

    params = load_json(PARAMS_FILE, {
        "balance": 1000,
        "risk_per_trade": 0.05,
        "take_profit": 0.02,
        "stop_loss": 0.01,
        "position_scale": 1.0
    })

    balance = float(account.get("balance", 1000.0))
    wins = int(account.get("wins", 0))
    losses = int(account.get("losses", 0))
    trades = max(1, int(account.get("trades", 1)))
    last_pnl = float(account.get("last_pnl", 0.0))

    winrate = wins / trades

    risk = float(params.get("risk_per_trade", 0.05))
    tp = float(params.get("take_profit", 0.02))
    sl = float(params.get("stop_loss", 0.01))
    scale = float(params.get("position_scale", 1.0))

    # If losing money overall, tighten everything
    if balance < 1000 or winrate < 0.52:
        risk *= 0.85
        scale *= 0.9
        tp *= 0.95
        sl *= 0.85

    # If last trade was a loss, tighten again
    if last_pnl < 0:
        risk *= 0.9
        scale *= 0.9

    # If clearly winning, allow mild expansion
    if balance > 1020 and winrate > 0.56 and last_pnl > 0:
        risk *= 1.05
        scale *= 1.05
        tp *= 1.03

    params["balance"] = round(balance, 2)
    params["risk_per_trade"] = max(0.01, min(0.08, risk))
    params["take_profit"] = max(0.005, min(0.03, tp))
    params["stop_loss"] = max(0.005, min(0.02, sl))
    params["position_scale"] = max(0.75, min(1.75, scale))

    save_json(PARAMS_FILE, params)
    return params

if __name__ == "__main__":
    print(apply_lock_profit_mode())

