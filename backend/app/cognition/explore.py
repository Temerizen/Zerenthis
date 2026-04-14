import json
import os
import random
import time
from typing import Dict, Any

DATA_PATH = "backend/data/exploration_state.json"

def _default_state() -> Dict[str, Any]:
    return {
        "history": [],
        "strategies": {},
        "curiosity_bias": 1.0,
        "last_action": None,
    }

def _load() -> Dict[str, Any]:
    state = _default_state()

    if not os.path.exists(DATA_PATH):
        return state

    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        if isinstance(loaded, dict):
            state.update(loaded)
    except Exception:
        return state

    if not isinstance(state.get("history"), list):
        state["history"] = []
    if not isinstance(state.get("strategies"), dict):
        state["strategies"] = {}
    if not isinstance(state.get("curiosity_bias"), (int, float)):
        state["curiosity_bias"] = 1.0
    if "last_action" not in state:
        state["last_action"] = None

    return state

def _save(data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _uncertainty_score(world_model: Dict[str, Any]) -> float:
    patterns = world_model.get("patterns", [])
    if not isinstance(patterns, list) or not patterns:
        return 1.0
    return max(0.1, 1.0 - min(len(patterns) / 50.0, 0.9))

def _strategy_score(state: Dict[str, Any], strategy: str) -> float:
    stats = state.get("strategies", {}).get(strategy, {"tries": 1, "success": 0})
    tries = stats.get("tries", 1)
    success = stats.get("success", 0)
    if not isinstance(tries, int) or tries <= 0:
        tries = 1
    if not isinstance(success, int) or success < 0:
        success = 0
    return success / tries

def _update_strategy(state: Dict[str, Any], strategy: str, success: bool) -> None:
    strategies = state.setdefault("strategies", {})
    current = strategies.get(strategy, {"tries": 0, "success": 0})

    tries = current.get("tries", 0)
    wins = current.get("success", 0)

    if not isinstance(tries, int) or tries < 0:
        tries = 0
    if not isinstance(wins, int) or wins < 0:
        wins = 0

    tries += 1
    if success:
        wins += 1

    strategies[strategy] = {"tries": tries, "success": wins}

def run(context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    context = context or {}
    state = _load()

    world_model = context.get("world_model", {})
    if not isinstance(world_model, dict):
        world_model = {}

    self_model = context.get("self_model", {})
    if not isinstance(self_model, dict):
        self_model = {}

    uncertainty = _uncertainty_score(world_model)
    confidence = self_model.get("confidence", 0.5)
    if not isinstance(confidence, (int, float)):
        confidence = 0.5

    exploration_drive = uncertainty * (1.2 - confidence)

    strategies = [
        "test_new_action",
        "repeat_successful",
        "modify_known",
        "probe_unknown",
        "stress_test",
    ]

    scored = []
    for s in strategies:
        base = random.random()
        performance = _strategy_score(state, s)
        score = base + (exploration_drive * (1 - performance))
        scored.append((s, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    chosen = scored[0][0]

    success = random.random() > 0.4
    _update_strategy(state, chosen, success)

    state["last_action"] = chosen
    state["history"].append({
        "time": time.time(),
        "strategy": chosen,
        "uncertainty": uncertainty,
        "confidence": confidence,
        "success": success,
    })
    state["history"] = state["history"][-200:]

    _save(state)

    return {
        "chosen_strategy": chosen,
        "uncertainty": uncertainty,
        "confidence": confidence,
        "exploration_drive": exploration_drive,
        "success": success,
        "strategies": state["strategies"],
        "history_size": len(state["history"]),
    }
