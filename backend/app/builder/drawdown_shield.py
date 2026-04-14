import json, os

ACCOUNT_FILE = "backend/data/paper_account.json"
PARAMS_FILE = "backend/data/market_params.json"
STATE_FILE = "backend/data/risk_state.json"

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def apply_drawdown_shield():
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

    state = load_json(STATE_FILE, {
        "peak_balance": 1000.0,
        "loss_streak": 0
    })

    balance = float(account.get("balance", 1000.0))
    last_pnl = float(account.get("last_pnl", 0.0))

    peak_balance = max(float(state.get("peak_balance", 1000.0)), balance)
    state["peak_balance"] = peak_balance

    if last_pnl < 0:
        state["loss_streak"] = int(state.get("loss_streak", 0)) + 1
    else:
        state["loss_streak"] = 0

    drawdown_pct = 0.0
    if peak_balance > 0:
        drawdown_pct = (peak_balance - balance) / peak_balance

    risk = float(params.get("risk_per_trade", 0.05))
    tp = float(params.get("take_profit", 0.02))
    sl = float(params.get("stop_loss", 0.01))
    scale = float(params.get("position_scale", 1.0))

    # Base sync
    params["balance"] = round(balance, 2)

    # Drawdown shield tiers
    if drawdown_pct >= 0.03:
        risk *= 0.85
        scale *= 0.85
        tp *= 0.97
        sl *= 0.92

    if drawdown_pct >= 0.06:
        risk *= 0.75
        scale *= 0.80
        tp *= 0.95
        sl *= 0.88

    if drawdown_pct >= 0.10:
        risk *= 0.60
        scale *= 0.70
        tp *= 0.92
        sl *= 0.85

    # Loss streak defense
    if state["loss_streak"] >= 2:
        risk *= 0.90
        scale *= 0.92

    if state["loss_streak"] >= 4:
        risk *= 0.80
        scale *= 0.85

    # Recovery mode: only re-expand gently near peak
    if drawdown_pct < 0.015 and state["loss_streak"] == 0 and last_pnl > 0:
        risk *= 1.01
        scale *= 1.01

    params["risk_per_trade"] = max(0.01, min(0.12, risk))
    params["take_profit"] = max(0.006, min(0.03, tp))
    params["stop_loss"] = max(0.005, min(0.02, sl))
    params["position_scale"] = max(0.75, min(2.50, scale))

    save_json(PARAMS_FILE, params)
    save_json(STATE_FILE, state)

    return {
        "balance": balance,
        "peak_balance": peak_balance,
        "drawdown_pct": round(drawdown_pct, 4),
        "loss_streak": state["loss_streak"],
        "params": params
    }

if __name__ == "__main__":
    print(apply_drawdown_shield())

