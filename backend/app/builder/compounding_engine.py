import json, os

ACCOUNT_FILE = "backend/data/paper_account.json"
PARAMS_FILE = "backend/data/market_params.json"
BASELINE_BALANCE = 1000.0

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def apply_compounding():
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

    balance = float(account.get("balance", BASELINE_BALANCE))
    wins = int(account.get("wins", 0))
    losses = int(account.get("losses", 0))
    trades = max(1, int(account.get("trades", 1)))
    last_pnl = float(account.get("last_pnl", 0.0))

    winrate = wins / trades
    equity_gain = balance / BASELINE_BALANCE

    risk = float(params.get("risk_per_trade", 0.05))
    tp = float(params.get("take_profit", 0.02))
    sl = float(params.get("stop_loss", 0.01))
    scale = float(params.get("position_scale", 1.0))

    # Base account sync
    params["balance"] = round(balance, 2)

    # --- Growth mode ---
    # Only compound if account is above baseline and behavior is healthy
    if balance > BASELINE_BALANCE and winrate >= 0.53:
        risk *= 1.02
        scale *= 1.03

    # --- Strong growth mode ---
    if balance > 1100 and winrate >= 0.55 and last_pnl > 0:
        risk *= 1.03
        scale *= 1.05
        tp *= 1.02

    # --- Drawdown defense ---
    if balance < 1050:
        risk *= 0.96
        scale *= 0.95

    # --- Loss defense ---
    if last_pnl < 0:
        risk *= 0.92
        scale *= 0.93
        sl *= 0.97

    # --- Winrate defense ---
    if winrate < 0.50:
        risk *= 0.90
        scale *= 0.90
        tp *= 0.97

    # Clamp to sane bounds
    params["risk_per_trade"] = max(0.015, min(0.12, risk))
    params["take_profit"] = max(0.006, min(0.03, tp))
    params["stop_loss"] = max(0.005, min(0.02, sl))
    params["position_scale"] = max(0.90, min(2.50, scale))

    save_json(PARAMS_FILE, params)
    return params

if __name__ == "__main__":
    print(apply_compounding())

