import json
import os
import time

CONTROL_STATE = os.path.join("backend","data","control_state.json")

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def run_kill_switch():
    state = load_json(CONTROL_STATE, {})

    balance = state.get("balance", 0)
    peak = state.get("peak_balance", balance)
    loss_streak = state.get("loss_streak", 0)

    # Calculate drawdown
    drawdown = 0
    if peak > 0:
        drawdown = (peak - balance) / peak

    # =========================
    # RULES
    # =========================
    kill = False
    reason = None

    # Rule 1: Hard drawdown
    if drawdown >= 0.20:
        kill = True
        reason = "drawdown_20_percent"

    # Rule 2: Loss streak
    elif loss_streak >= 5:
        kill = True
        reason = "loss_streak_5"

    # Rule 3: Unknown regime
    regime = state.get("regime", {}).get("regime", "UNKNOWN")
    if regime == "UNKNOWN":
        kill = True
        reason = "unknown_regime"

    # =========================
    # ACTION
    # =========================
    result = {
        "kill_active": kill,
        "reason": reason,
        "drawdown": drawdown,
        "loss_streak": loss_streak,
        "timestamp": int(time.time())
    }

    # Inject into state
    state["kill_switch"] = result

    # If kill active → reduce risk massively
    if kill:
        params = state.get("final_params", {})
        params["risk_per_trade"] = 0.002
        params["position_scale"] = 0.25
        state["final_params"] = params

    save_json(CONTROL_STATE, state)

    return result

