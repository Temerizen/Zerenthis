from __future__ import annotations

from typing import Any, Dict, List

def _default_target(context: Dict[str, Any] | None = None) -> str:
    context = context or {}
    target = context.get("target")
    if isinstance(target, str) and target and target != "assets":
        return target
    return "backend/app/engines/offer_engine.py"

def detect_builder_need(context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    context = context or {}
    return {
        "should_build": True,
        "reason": "fallback_trigger",
        "target": _default_target(context),
    }

def detect_builder_need_with_queue(
    context: Dict[str, Any] | None = None,
    queue: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    context = context or {}
    queue = queue or []

    chosen_target = _default_target(context)

    for item in queue:
        if not isinstance(item, dict):
            continue
        candidate = item.get("target")
        if isinstance(candidate, str) and candidate and candidate != "assets":
            chosen_target = candidate
            break

    return {
        "should_build": True,
        "reason": "queue_fallback_trigger",
        "target": chosen_target,
        "queue_size": len(queue),
    }
