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

def enforce_live_params():
    account = load_json(ACCOUNT_FILE, {
        "balance": 1000.0,
        "wins": 0,
        "losses": 0,
        "trades": 0,
        "last_pnl": 0.0
    })

    params = load_json(PARAMS_FILE, {
        "balance": 1000.0,
        "risk_per_trade": 0.05,
        "take_profit": 0.02,
        "stop_loss": 0.01,
        "position_scale": 1.0
    })

    balance = float(account.get("balance", 1000.0))
    params["balance"] = round(balance, 2)

    params["risk_per_trade"] = max(0.015, min(0.12, float(params.get("risk_per_trade", 0.05))))
    params["take_profit"] = max(0.006, min(0.03, float(params.get("take_profit", 0.02))))
    params["stop_loss"] = max(0.005, min(0.02, float(params.get("stop_loss", 0.01))))
    params["position_scale"] = max(0.90, min(2.50, float(params.get("position_scale", 1.0))))

    save_json(PARAMS_FILE, params)
    return params

if __name__ == "__main__":
    print(enforce_live_params())
