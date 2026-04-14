from __future__ import annotations

from typing import Any, Dict
from backend.app.cognition.task_memory import is_on_cooldown, choose_alternate

def apply_task_cooldown(selected_task: Dict[str, Any] | None = None) -> Dict[str, Any]:
    selected_task = selected_task or {}
    task = str(selected_task.get("task", "unknown"))
    goal = str(selected_task.get("goal", "balanced_progression"))

    if is_on_cooldown(task):
        alt = choose_alternate(task)
        return {
            "status": "cooldown_redirect",
            "selected": {
                "task": alt,
                "goal": goal,
                "type": "cooldown_redirect",
                "reason": f"task_on_cooldown:{task}",
            },
            "original_task": task,
            "cooldown_task": task,
            "redirect_task": alt,
        }

    return {
        "status": "ok",
        "selected": selected_task,
        "original_task": task,
    }
