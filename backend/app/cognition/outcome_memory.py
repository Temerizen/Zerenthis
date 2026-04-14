import json
import os
from typing import Any, Dict

OUTCOME_PATH = "backend/data/task_outcomes.json"

def _load() -> Dict[str, Any]:
    if not os.path.exists(OUTCOME_PATH):
        return {"tasks": {}}
    try:
        with open(OUTCOME_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {"tasks": {}}
    except Exception:
        return {"tasks": {}}

def _save(data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(OUTCOME_PATH), exist_ok=True)
    with open(OUTCOME_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def record_outcome(task: str, success: float) -> Dict[str, Any]:
    data = _load()
    tasks = data.setdefault("tasks", {})

    entry = tasks.setdefault(task, {
        "success": 0.0,
        "fail": 0.0,
        "runs": 0
    })

    entry["runs"] += 1
    if success >= 0:
        entry["success"] += float(success)
    else:
        entry["fail"] += abs(float(success))

    _save(data)
    return entry

def score_task(task: str) -> float:
    data = _load()
    entry = data.get("tasks", {}).get(task)

    if not isinstance(entry, dict):
        return 0.0

    total = float(entry.get("success", 0.0)) - float(entry.get("fail", 0.0))
    runs = int(entry.get("runs", 0))
    return total / max(runs, 1)
