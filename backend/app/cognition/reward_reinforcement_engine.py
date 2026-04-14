import json
import os

OUTCOME_PATH = "backend/data/task_outcomes.json"

def _load():
    if not os.path.exists(OUTCOME_PATH):
        return {"tasks": {}}
    try:
        with open(OUTCOME_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {"tasks": {}}
    except Exception:
        return {"tasks": {}}

def get_reward_bias(task: str) -> float:
    data = _load()
    stats = data.get("tasks", {}).get(task, {})

    if not isinstance(stats, dict):
        return 0.0

    success = float(stats.get("success", 0) or 0)
    fail = float(stats.get("fail", 0) or 0)
    runs = int(stats.get("runs", 0) or 0)
    total = success + fail

    if runs < 3 or total <= 0:
        return 0.0

    ratio = (success - fail) / max(1.0, total)
    return max(-0.2, min(0.2, ratio * 0.2))
