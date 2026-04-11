
import json
import os
from collections import Counter
from datetime import datetime

STATE_PATH = "backend/data/intelligence_state.json"

def load_state():
    if not os.path.exists(STATE_PATH):
        return {"observations": [], "scores": {}}
    with open(STATE_PATH, "r") as f:
        return json.load(f)

def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

# =========================
# OBSERVER (UPGRADED)
# =========================

def observe_system(signal: dict):
    state = load_state()

    observation = {
        "time": datetime.utcnow().isoformat(),
        "signal": signal
    }

    state["observations"].append(observation)

    # Keep last 200 observations
    state["observations"] = state["observations"][-200:]

    # Update scoring
    topic = signal.get("topic")
    score = signal.get("score", 1)

    if topic:
        state["scores"][topic] = state["scores"].get(topic, 0) + score

    save_state(state)

    return {
        "status": "observation_recorded",
        "total_observations": len(state["observations"]),
        "tracked_topics": len(state["scores"])
    }

# =========================
# BUILDER (INTELLIGENT)
# =========================

def build_intelligent_topic():

    state = load_state()
    scores = state.get("scores", {})

    if not scores:
        return {"topic": "high_value_ai_system"}

    # Rank topics by score
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    best_topic = ranked[0][0]

    topic = f"Ultimate {best_topic} System That Dominates Results"

    return {
        "status": "intelligent_topic_generated",
        "topic": topic,
        "based_on": best_topic
    }

# =========================
# SIMULATOR (UPGRADED)
# =========================

def simulate_outcome(topic: str):

    state = load_state()
    scores = state.get("scores", {})

    base_score = scores.get(topic, 5)

    # Normalize score
    predicted = round(min(9.9, max(5.0, base_score / 2 + 5)), 2)

    verdict = "approve" if predicted >= 7.5 else "reject"

    return {
        "status": "simulation_complete",
        "topic": topic,
        "predicted_score": predicted,
        "verdict": verdict
    }

