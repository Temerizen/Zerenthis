import json
import os
import time
from typing import Dict, Any, List

THOUGHT_PATH = "backend/data/thought_state.json"

DEFAULT_STATE = {
    "active_thought": None,
    "thought_chain": [],
    "history": []
}

MAX_CHAIN = 12
MAX_HISTORY = 200
STAGNATION_WINDOW = 4


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


def _base_focus(simulation: Dict[str, Any]) -> str:
    return simulation.get("chosen_action") or simulation.get("action") or "none"


def _score(simulation: Dict[str, Any]) -> float:
    try:
        return float(simulation.get("score") or simulation.get("confidence") or 0.5)
    except Exception:
        return 0.5


def _mutate_focus(goal: str, focus: str, score: float) -> str:
    mutation_map = {
        "expand_capability": [
            "integrate_learnings",
            "test_variations",
            "scan_new_options",
            "capture_learnings"
        ],
        "optimize_and_scale": [
            "lock_pattern",
            "optimize_efficiency",
            "repeat_success",
            "scale_execution"
        ],
        "rebalance_behavior": [
            "increase_exploration",
            "reduce_persistence",
            "maintain_balance",
            "introduce_variation"
        ],
        "introduce_variation": [
            "test_variations",
            "scan_new_options",
            "introduce_variation",
            "capture_learnings"
        ],
        "maintain_stability": [
            "maintain_balance",
            "stabilize_system",
            "reduce_variance"
        ]
    }

    candidates = mutation_map.get(goal, [focus, "test_variations", "scan_new_options"])
    if focus not in candidates:
        candidates.insert(0, focus)

    idx = candidates.index(focus) if focus in candidates else 0

    if score >= 1.2:
        next_idx = min(idx + 1, len(candidates) - 1)
        return candidates[next_idx]

    if score < 0.8:
        return candidates[0]

    if idx + 1 < len(candidates):
        return candidates[idx + 1]

    return candidates[0]


def _detect_stagnation(chain: List[Dict[str, Any]]) -> bool:
    if len(chain) < STAGNATION_WINDOW:
        return False
    recent = chain[-STAGNATION_WINDOW:]
    focuses = [item.get("focus", "none") for item in recent]
    return len(set(focuses)) == 1


def run(context: Dict[str, Any] | None = None):
    context = context or {}

    state = _load(THOUGHT_PATH, DEFAULT_STATE)

    goal = context.get("goal") or "maintain_stability"
    simulation = context.get("simulation") or {}

    base_focus = _base_focus(simulation)
    score = _score(simulation)

    chain = state.get("thought_chain", [])
    if not isinstance(chain, list):
        chain = []

    stagnating_before = _detect_stagnation(chain)

    final_focus = base_focus
    divergence_reason = "none"

    if stagnating_before and base_focus != "none":
        final_focus = _mutate_focus(goal, base_focus, score)
        if final_focus != base_focus:
            divergence_reason = "stagnation_mutation"

    new_thought = {
        "timestamp": time.time(),
        "goal": goal,
        "focus": final_focus,
        "base_focus": base_focus,
        "intent": f"advance_{goal}",
        "confidence": score,
        "divergence_reason": divergence_reason
    }

    chain.append(new_thought)
    chain = chain[-MAX_CHAIN:]

    evolving = False
    if len(chain) >= 2 and chain[-1].get("focus") != chain[-2].get("focus"):
        evolving = True

    stagnating_after = _detect_stagnation(chain)

    active_thought = {
        "current_focus": new_thought["focus"],
        "base_focus": base_focus,
        "goal": goal,
        "depth": len(chain),
        "evolving": evolving,
        "stagnating": stagnating_after,
        "divergence_reason": divergence_reason
    }

    history = state.get("history", [])
    if not isinstance(history, list):
        history = []

    history.append({
        "timestamp": time.time(),
        "chain_snapshot": chain,
        "stagnating": stagnating_after
    })
    history = history[-MAX_HISTORY:]

    new_state = {
        "active_thought": active_thought,
        "thought_chain": chain,
        "history": history
    }

    _save(THOUGHT_PATH, new_state)

    return {
        "status": "thought_active",
        "focus": active_thought["current_focus"],
        "base_focus": active_thought["base_focus"],
        "depth": active_thought["depth"],
        "evolving": evolving,
        "stagnating": stagnating_after,
        "divergence_reason": divergence_reason
    }
