import json
import os
import time
from typing import Any, Dict

OUTCOME_PATH = "backend/data/task_outcomes.json"
EVOLUTION_PATH = "backend/data/evolution_state.json"

DEFAULT_EVOLUTION_STATE: Dict[str, Any] = {
    "task_weights": {},
    "intent_bias": {},
    "failure_decay": {},
    "strategy_patterns": [],
    "last_updated": 0,
}

def _safe_load(path: str, default: Dict[str, Any]) -> Dict[str, Any]:
    if not os.path.exists(path):
        return default.copy()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else default.copy()
    except Exception:
        return default.copy()

def _safe_save(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_evolution_state() -> Dict[str, Any]:
    state = _safe_load(EVOLUTION_PATH, DEFAULT_EVOLUTION_STATE)
    for key, fallback in DEFAULT_EVOLUTION_STATE.items():
        if key not in state:
            state[key] = fallback.copy() if isinstance(fallback, dict) else list(fallback) if isinstance(fallback, list) else fallback
    return state

def _clamp_weight(value: float) -> float:
    return max(0.25, min(3.0, round(value, 4)))

def _append_strategy_pattern(state: Dict[str, Any], task: str, success_rate: float, total: int) -> None:
    patterns = state.setdefault("strategy_patterns", [])
    latest = None
    for item in reversed(patterns):
        if isinstance(item, dict) and item.get("task") == task:
            latest = item
            break

    if latest and latest.get("success_rate") == round(success_rate, 4) and latest.get("total") == total:
        return

    patterns.append(
        {
            "task": task,
            "success_rate": round(success_rate, 4),
            "total": total,
            "timestamp": time.time(),
        }
    )

    if len(patterns) > 100:
        del patterns[:-100]

def run_evolution() -> Dict[str, Any]:
    outcomes = _safe_load(OUTCOME_PATH, {"tasks": {}})
    evo = load_evolution_state()

    tasks = outcomes.get("tasks", {})
    if not isinstance(tasks, dict):
        tasks = {}

    tasks_evaluated = 0
    tasks_updated = 0

    for task, stats in tasks.items():
        if not isinstance(task, str) or not isinstance(stats, dict):
            continue

        success = int(stats.get("success", 0) or 0)
        fail = int(stats.get("fail", 0) or 0)
        total = success + fail

        if total < 3:
            continue

        tasks_evaluated += 1
        success_rate = success / total

        current_weight = float(evo["task_weights"].get(task, 1.0))

        if success_rate > 0.7:
            current_weight *= 1.1
        elif success_rate < 0.3:
            current_weight *= 0.9

        new_weight = _clamp_weight(current_weight)
        previous_weight = evo["task_weights"].get(task)

        evo["task_weights"][task] = new_weight

        if previous_weight != new_weight:
            tasks_updated += 1

        current_decay = int(evo["failure_decay"].get(task, 0) or 0)
        if success_rate < 0.3:
            evo["failure_decay"][task] = min(20, current_decay + 1)
        else:
            evo["failure_decay"][task] = max(0, current_decay - 1)

        if success_rate > 0.8 and total >= 5:
            _append_strategy_pattern(evo, task, success_rate, total)

    evo["last_updated"] = time.time()
    _safe_save(EVOLUTION_PATH, evo)

    return {
        "status": "evolution_updated",
        "tasks_evaluated": tasks_evaluated,
        "tasks_updated": tasks_updated,
        "strategy_patterns": len(evo.get("strategy_patterns", [])),
        "timestamp": evo["last_updated"],
    }

if __name__ == "__main__":
    print(json.dumps(run_evolution(), indent=2))
