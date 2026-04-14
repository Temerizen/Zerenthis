import json, os, random, time

PERF_FILE = "backend/data/performance_log.json"
STATE_FILE = "backend/data/evo_state.json"

def load_perf():
    if not os.path.exists(PERF_FILE):
        return []
    return json.load(open(PERF_FILE, "r"))

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"streak": 0, "last_score": None}
    return json.load(open(STATE_FILE, "r"))

def save_state(s):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    json.dump(s, open(STATE_FILE, "w"), indent=2)

def is_stagnant(history):
    if len(history) < 5:
        return False

    recent = history[-5:]
    scores = [x for x in recent if isinstance(x, (int, float))]

    if len(scores) < 5:
        return False

    variance = max(scores) - min(scores)

    return variance < 0.5  # plateau threshold

def mutate_aggressive(params):
    p = params.copy()

    p["risk_per_trade"] = random.uniform(0.01, 0.2)
    p["take_profit"] = random.uniform(0.01, 0.05)
    p["stop_loss"] = random.uniform(0.005, 0.03)
    p["position_scale"] = random.uniform(0.5, 2.5)

    return p

def break_if_needed(current_params):
    history = load_perf()
    state = load_state()

    if not history:
        return current_params, False

    if is_stagnant(history):
        state["streak"] += 1
    else:
        state["streak"] = 0

    save_state(state)

    if state["streak"] >= 3:
        print("?? STAGNATION DETECTED ? FORCING EVOLUTION")

        mutated = mutate_aggressive(current_params)

        state["streak"] = 0
        save_state(state)

        return mutated, True

    return current_params, False
