import json
import os
import time
from typing import Dict, Any, List

SELF_GOAL_PATH = "backend/data/self_goal_state.json"
IDENTITY_PATH = "backend/data/identity_state.json"
SIM_PATH = "backend/data/simulation_state.json"

DEFAULT_STATE = {
    "last_simulation": None,
    "history": []
}

MAX_HISTORY = 100


def _load(path, default):
    if not os.path.exists(path):
        return default.copy()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return default.copy()
    except Exception:
        return default.copy()


def _save(path, state):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _simulate_options(goal: str, traits: Dict[str, Any]) -> List[Dict[str, Any]]:
    confidence = traits.get("confidence", 0.5)
    curiosity = traits.get("curiosity", 0.5)
    persistence = traits.get("persistence", 0.5)

    options = []

    if goal == "rebalance_behavior":
        options = [
            {"action": "increase_exploration", "score": curiosity + 0.2 - persistence * 0.1},
            {"action": "reduce_persistence", "score": 0.5 + (1 - persistence)},
            {"action": "maintain_balance", "score": confidence}
        ]

    elif goal == "expand_capability":
        options = [
            {"action": "explore_new_paths", "score": curiosity + 0.3},
            {"action": "test_variations", "score": curiosity + 0.2},
            {"action": "integrate_learnings", "score": confidence + persistence}
        ]

    elif goal == "optimize_and_scale":
        options = [
            {"action": "repeat_success", "score": persistence + 0.2},
            {"action": "optimize_efficiency", "score": confidence + 0.2},
            {"action": "lock_pattern", "score": persistence + confidence}
        ]

    else:
        options = [
            {"action": "maintain", "score": confidence}
        ]

    return options


def _choose_best(options: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not options:
        return {"action": "none", "score": 0}
    return max(options, key=lambda x: x.get("score", 0))


def run(context: Dict[str, Any] | None = None):
    context = context or {}

    goal_state = _load(SELF_GOAL_PATH, {"active_goal": "maintain_stability"})
    identity = _load(IDENTITY_PATH, {"traits": {}})
    state = _load(SIM_PATH, DEFAULT_STATE)

    goal = goal_state.get("active_goal", "maintain_stability")
    traits = identity.get("traits", {})

    options = _simulate_options(goal, traits)
    best = _choose_best(options)

    simulation = {
        "timestamp": time.time(),
        "goal": goal,
        "options": options,
        "chosen": best
    }

    history = state.get("history", [])
    if not isinstance(history, list):
        history = []

    history.append(simulation)
    history = history[-MAX_HISTORY:]

    new_state = {
        "last_simulation": simulation,
        "history": history
    }

    _save(SIM_PATH, new_state)

    return {
        "status": "simulation_complete",
        "goal": goal,
        "chosen_action": best.get("action"),
        "score": best.get("score"),
        "options_evaluated": len(options)
    }
