import json, os

PARAMS_FILE = "backend/data/market_params.json"

def load_params():
    if not os.path.exists(PARAMS_FILE):
        return None
    with open(PARAMS_FILE, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def override_params(res):
    params = load_params()
    if not params:
        return res

    for key in ["balance", "risk_per_trade", "take_profit", "stop_loss", "position_scale"]:
        if key in params:
            res["params"][key] = params[key]

    return res

