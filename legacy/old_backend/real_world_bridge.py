import requests, random, time, json, os, subprocess, sys

API = "http://127.0.0.1:8000/api/autopilot/step"
ACCOUNT_FILE = "backend/data/paper_account.json"
TRADE_LOG = "backend/data/paper_trade_log.json"
PARAMS_FILE = "backend/data/market_params.json"

def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_account():
    return load_json(ACCOUNT_FILE, {
        "balance": 1000.0,
        "wins": 0,
        "losses": 0,
        "trades": 0,
        "last_pnl": 0.0
    })

def save_account(account):
    save_json(ACCOUNT_FILE, account)

def append_trade(trade):
    trades = load_json(TRADE_LOG, [])
    trades.append(trade)
    save_json(TRADE_LOG, trades[-500:])

def get_price():
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
            timeout=10
        )
        return float(r.json()["bitcoin"]["usd"])
    except:
        return float(50000 + random.randint(-1000, 1000))

def clamp_live_params(res, balance):
    p = dict(res["params"])

    p["balance"] = round(float(balance), 2)
    p["risk_per_trade"] = max(0.015, min(0.12, float(p.get("risk_per_trade", 0.05))))
    p["take_profit"] = max(0.006, min(0.03, float(p.get("take_profit", 0.02))))
    p["stop_loss"] = max(0.005, min(0.02, float(p.get("stop_loss", 0.01))))
    p["position_scale"] = max(0.90, min(2.50, float(p.get("position_scale", 1.0))))

    save_json(PARAMS_FILE, p)
    res["params"] = p
    return res

def simulate_trade(params, balance):
    price = get_price()
    direction = random.choice(["long", "short"])

    risk = float(params["risk_per_trade"])
    tp = float(params["take_profit"])
    sl = float(params["stop_loss"])
    scale = float(params["position_scale"])

    move = random.uniform(-sl, tp)
    pnl = balance * risk * move * scale

    return {
        "timestamp": time.time(),
        "price": price,
        "direction": direction,
        "move": move,
        "pnl": pnl,
        "risk_per_trade": risk,
        "take_profit": tp,
        "stop_loss": sl,
        "position_scale": scale
    }

while True:
    account = load_account()
    balance = float(account["balance"])

    res = requests.post(API, timeout=30).json()
    res = clamp_live_params(res, balance)

    params = res["params"]
    trade = simulate_trade(params, balance)

    account["balance"] = round(balance + float(trade["pnl"]), 2)
    account["trades"] += 1
    account["last_pnl"] = round(float(trade["pnl"]), 2)

    if trade["pnl"] >= 0:
        account["wins"] += 1
    else:
        account["losses"] += 1

    save_account(account)

    trade_record = {
        "decision": res.get("decision"),
        "score": res.get("score"),
        "balance_after": account["balance"],
        **trade
    }
    append_trade(trade_record)

    print(
        f"[TRADE {account['trades']}] "
        f"{trade['direction'].upper()} @ {round(trade['price'],2)} | "
        f"PnL: {round(trade['pnl'],2)} | "
        f"BAL: {account['balance']} | "
        f"W/L: {account['wins']}/{account['losses']} | "
        f"risk: {round(params['risk_per_trade'],4)} | "
        f"scale: {round(params['position_scale'],4)} | "
        f"decision: {res.get('decision')}"
    )

    time.sleep(2)
