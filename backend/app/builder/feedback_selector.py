from __future__ import annotations
import json
from pathlib import Path

FEEDBACK_PATH = Path("backend/data/builder/feedback_log.json")

def _load_feedback() -> list:
    if FEEDBACK_PATH.exists():
        try:
            return json.loads(FEEDBACK_PATH.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def _normalize_target(target) -> str:
    if isinstance(target, list):
        for item in target:
            if isinstance(item, str) and item.strip():
                return item.strip()
        return ""
    if isinstance(target, str):
        return target.strip()
    return ""

def build_target_stats() -> dict:
    rows = _load_feedback()
    stats: dict = {}

    for row in rows:
        target = ""
        if isinstance(row, dict):
            target = _normalize_target(((row.get("request") or {}).get("target", "")))

            if not target:
                summary = row.get("plan_summary", "")
                if isinstance(summary, str) and "target=" in summary:
                    try:
                        target = summary.split("target=", 1)[1].split("|", 1)[0].strip()
                    except Exception:
                        target = ""

        if not target:
            continue

        if target not in stats:
            stats[target] = {"successes": 0, "failures": 0}

        if row.get("success"):
            stats[target]["successes"] += 1
        else:
            stats[target]["failures"] += 1

    return stats

def choose_strategy_for_target(target) -> dict:
    target_path = _normalize_target(target)
    if not target_path:
        return {
            "strategy": "baseline",
            "reason": "no_history",
            "cooldown": False,
        }

    stats = build_target_stats()
    row = stats.get(target_path, {"successes": 0, "failures": 0})

    successes = int(row.get("successes", 0))
    failures = int(row.get("failures", 0))

    if successes == 0 and failures == 0:
        return {
            "strategy": "baseline",
            "reason": "no_history",
            "cooldown": False,
        }

    if failures > successes:
        return {
            "strategy": "stabilize",
            "reason": "failures_meet_or_exceed_successes",
            "cooldown": True,
        }

    return {
        "strategy": "optimize" if successes >= 1 else "baseline",
        "reason": "previous_success_detected",
        "cooldown": False,
    }
