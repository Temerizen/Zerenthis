import json
import os

EVOLUTION_PATH = "backend/data/evolution_state.json"
OUTCOME_PATH = "backend/data/task_outcomes.json"

def _load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else default
    except Exception:
        return default

def get_failure_penalty(task: str) -> float:
    evo = _load_json(EVOLUTION_PATH, {})
    outcomes = _load_json(OUTCOME_PATH, {"tasks": {}})

    decay = float(evo.get("failure_decay", {}).get(task, 0) or 0)

    stats = outcomes.get("tasks", {}).get(task, {})
    if not isinstance(stats, dict):
        stats = {}

    fail = float(stats.get("fail", 0) or 0)
    success = float(stats.get("success", 0) or 0)
    total = success + fail

    fail_pressure = 0.0
    if total > 0:
        fail_pressure = fail / total

    penalty = (decay * 0.03) + (fail_pressure * 0.12)
    return max(0.0, min(0.35, penalty))
