import time
import json
from pathlib import Path

LOG_PATH = Path("backend/data/task_log.json")

def load_log():
    if LOG_PATH.exists():
        try:
            return json.load(open(LOG_PATH, "r", encoding="utf-8"))
        except:
            return []
    return []

def recent_task_counts(log, limit=10):
    counts = {}
    for item in log[-limit:]:
        task = None

        if isinstance(item, dict):
            result = item.get("result", {})
            task_obj = item.get("task", {})

            if isinstance(result, dict):
                task = result.get("task")

            if not task and isinstance(task_obj, dict):
                task = task_obj.get("task")

        if task:
            counts[task] = counts.get(task, 0) + 1

    return counts

def build_priority():
    base_candidates = [
        {
            "task": "toolbox_strategy",
            "base_score": 95,
            "reason": "highest leverage systems first"
        },
        {
            "task": "builder_handoff",
            "base_score": 88,
            "reason": "improve proof and reality feedback"
        },
        {
            "task": "revenue_scan",
            "base_score": 72,
            "reason": "useful, but after toolbox direction is clear"
        }
    ]

    log = load_log()
    counts = recent_task_counts(log, limit=10)

    ranked = []
    for candidate in base_candidates:
        task = candidate["task"]
        repeats = counts.get(task, 0)

        # V49 memory weighting:
        # each recent repeat applies a cooldown penalty
        penalty = repeats * 18
        score = max(1, candidate["base_score"] - penalty)

        ranked.append({
            "task": task,
            "score": score,
            "base_score": candidate["base_score"],
            "recent_repeats": repeats,
            "penalty": penalty,
            "reason": candidate["reason"]
        })

    ranked = sorted(ranked, key=lambda x: x["score"], reverse=True)
    top = ranked[0] if ranked else None

    return {
        "status": "ok",
        "timestamp": time.time(),
        "ranked": ranked,
        "next_action": top
    }
