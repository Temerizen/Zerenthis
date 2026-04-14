from __future__ import annotations

import json
import os
from typing import Any, Dict

COMPLETED_PATH = "backend/data/autonomy/completed_tasks.json"

def _load() -> Dict[str, Any]:
    if not os.path.exists(COMPLETED_PATH):
        return {}
    try:
        with open(COMPLETED_PATH, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def _save(data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(COMPLETED_PATH), exist_ok=True)
    with open(COMPLETED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def is_completed(task: str) -> bool:
    data = _load()
    item = data.get(task, {})
    return bool(item.get("completed", False)) if isinstance(item, dict) else bool(item)

def mark_completed(task: str, route: str = "", goal: str = "") -> Dict[str, Any]:
    data = _load()
    data[task] = {
        "completed": True,
        "route": route,
        "goal": goal,
    }
    _save(data)
    return data[task]
