from __future__ import annotations
import json
import time
from pathlib import Path
from backend.app.builder.target_scorer import update_target_memory

FEEDBACK_PATH = Path("backend/data/builder/feedback_log.json")

def _load() -> list:
    if FEEDBACK_PATH.exists():
        return json.loads(FEEDBACK_PATH.read_text(encoding="utf-8"))
    return []

def _save(items: list) -> None:
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    FEEDBACK_PATH.write_text(json.dumps(items, indent=2), encoding="utf-8")

def log_builder_feedback(request_data: dict, patch_plan: dict, apply_result: dict) -> dict:
    items = _load()
    success = apply_result.get("status") == "applied"
    target_path = ""
    changes = patch_plan.get("changes", [])
    if isinstance(changes, list) and changes:
        first_change = changes[0] or {}
        target_path = first_change.get("file", "")

    memory_row = update_target_memory(target_path, success) if target_path else {}

    row = {
        "timestamp": int(time.time()),
        "request": {
            **request_data,
            "strategy": patch_plan.get("strategy", "baseline"),
            "strategy_reason": patch_plan.get("strategy_reason", "")
        },
        "plan_summary": patch_plan.get("summary", ""),
        "target_path": target_path,
        "target_score": patch_plan.get("target_score", {}),
        "simulation": patch_plan.get("simulation", {}),
        "result": apply_result,
        "success": success,
        "memory_after": memory_row
    }
    items.append(row)
    _save(items)
    return row
