import json
import random
import os

ACCOUNT_FILE = "backend/data/paper_account.json"
STREAK_FILE = "backend/data/streak_state.json"

def _load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        except:
            return default.copy()
    return default.copy()

def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _load_account():
    return _load_json(ACCOUNT_FILE, {
        "balance": 50.0,
        "wins": 0,
        "losses": 0,
        "trades": 0,
        "last_pnl": 0.0
    })

def _save_account(acc):
    _save_json(ACCOUNT_FILE, acc)

def _load_streak():
    return _load_json(STREAK_FILE, {
        "win_streak": 0,
        "loss_streak": 0
    })

def _save_streak(state):
    _save_json(STREAK_FILE, state)

def run_paper_trades(data, signals):
    account = _load_account()
    streak = _load_streak()

    trades = []

    if not isinstance(signals, list):
        signals = []

    valid_signals = [s for s in signals if isinstance(s, dict)]

    for signal in valid_signals:
        price = float(signal.get("price", 0) or 0)
        if price <= 0:
            continue

        confidence = float(signal.get("confidence", 1.0) or 1.0)
        strategy = signal.get("strategy", "conservative")

        # Base pnl generator
        pnl = random.uniform(-0.005, 0.005)

        # Confidence scaling
        if confidence > 2.0:
            pnl *= 2.0
        elif confidence > 1.5:
            pnl *= 1.5

        # Streak intelligence
        if streak["win_streak"] >= 3:
            pnl *= 1.5
        elif streak["loss_streak"] >= 2:
            pnl *= 0.5

        pnl = round(pnl, 4)
        exit_price = round(price * (1 + pnl), 4)

        trade = {
            "asset": signal.get("asset"),
            "action": signal.get("action", "BUY"),
            "entry": price,
            "exit": exit_price,
            "pnl": pnl,
            "reason": signal.get("reason", "signal_trade"),
            "strategy": strategy,
            "confidence": confidence
        }

        trades.append(trade)

        account["balance"] = round(account["balance"] + pnl, 10)
        account["trades"] += 1
        account["last_pnl"] = pnl

        if pnl > 0:
            account["wins"] += 1
            streak["win_streak"] += 1
            streak["loss_streak"] = 0
        else:
            account["losses"] += 1
            streak["loss_streak"] += 1
            streak["win_streak"] = 0

    # Hard fallback so learning never stalls
    if not trades and isinstance(data, list) and data:
        valid = [x for x in data if isinstance(x, dict) and x.get("price")]
        if valid:
            pick = random.choice(valid)
            price = float(pick.get("price", 100) or 100)
            pnl = round(random.uniform(-0.005, 0.005), 4)
            exit_price = round(price * (1 + pnl), 4)

            trade = {
                "asset": pick.get("asset"),
                "action": "BUY",
                "entry": price,
                "exit": exit_price,
                "pnl": pnl,
                "reason": "forced_fallback_trade",
                "strategy": "conservative",
                "confidence": 1.0
            }

            trades.append(trade)

            account["balance"] = round(account["balance"] + pnl, 10)
            account["trades"] += 1
            account["last_pnl"] = pnl

            if pnl > 0:
                account["wins"] += 1
                streak["win_streak"] += 1
                streak["loss_streak"] = 0
            else:
                account["losses"] += 1
                streak["loss_streak"] += 1
                streak["win_streak"] = 0

    _save_account(account)
    _save_streak(streak)
    return trades
