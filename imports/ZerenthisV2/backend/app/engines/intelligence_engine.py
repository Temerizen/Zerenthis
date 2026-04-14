import json
import os

STATE_FILE = os.path.join("backend","data","intelligence_state.json")
PERF_FILE = os.path.join("backend","data","perf_window.json")

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"confidence_threshold": 1.25}
    return json.load(open(STATE_FILE, "r", encoding="utf-8-sig"))

def save_state(state):
    json.dump(state, open(STATE_FILE, "w"), indent=2)

def load_perf():
    if not os.path.exists(PERF_FILE):
        return {"recent_pnl": []}
    return json.load(open(PERF_FILE, "r", encoding="utf-8-sig"))

def run_intelligence():
    state = load_state()
    perf = load_perf()

    recent = perf.get("recent_pnl", [])[-20:]
    if len(recent) < 10:
        return {"status": "not_enough_data"}

    avg = sum(recent)/len(recent)

    # adaptive logic
    if avg < 0:
        state["confidence_threshold"] = min(1.6, state["confidence_threshold"] + 0.05)
    else:
        state["confidence_threshold"] = max(1.05, state["confidence_threshold"] - 0.02)

    save_state(state)

    return {
        "status": "adjusted",
        "new_threshold": state["confidence_threshold"],
        "avg_recent_pnl": avg
    }
