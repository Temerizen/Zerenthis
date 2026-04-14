from __future__ import annotations
from pathlib import Path
from backend.app.builder.feedback_selector import choose_strategy_for_target
from backend.app.builder.target_scorer import choose_best_target, score_target
from backend.app.builder.patch_simulator import simulate_patch
from backend.app.builder.target_discovery import discover_targets

def _traffic_engine_content(strategy: str) -> str:
    if strategy == "stabilize":
        return """from __future__ import annotations

def run(payload: dict | None = None) -> dict:
    payload = payload or {}
    return {
        "status": "ok",
        "engine": "traffic_engine",
        "mode": "stabilize",
        "message": "Stability-focused traffic engine patch is active",
        "input": payload
    }
"""
    if strategy == "optimize":
        return """from __future__ import annotations

def run(payload: dict | None = None) -> dict:
    payload = payload or {}
    items = payload.get("items", [])
    return {
        "status": "ok",
        "engine": "traffic_engine",
        "mode": "optimize",
        "message": "Optimization-focused traffic engine patch is active",
        "input_size": len(items) if isinstance(items, list) else 0,
        "input": payload
    }
"""
    return """from __future__ import annotations

def run(payload: dict | None = None) -> dict:
    payload = payload or {}
    return {
        "status": "ok",
        "engine": "traffic_engine",
        "mode": "baseline",
        "message": "Builder baseline traffic engine patch is active",
        "input": payload
    }
"""

def _generic_content(target_path: str, strategy: str) -> str:
    stem = Path(target_path).stem
    return f"""from __future__ import annotations

def run(payload: dict | None = None) -> dict:
    payload = payload or {{}}
    return {{
        "status": "ok",
        "engine": "{stem}",
        "mode": "{strategy}",
        "message": "Builder generated {strategy} patch for {Path(target_path).name}",
        "input": payload
    }}
"""

def _normalize_target(goal: str, target: str | list[str] | None) -> tuple[str, dict]:
    if isinstance(target, list) and target:
        decision = choose_best_target([Path(t).as_posix() for t in target])
        return decision.get("target", ""), decision

    if isinstance(target, str) and target.strip():
        target_path = Path(str(target)).as_posix()
        return target_path, {"target": target_path, "score": score_target(target_path)["score"], "source": "direct_target"}

    discovered = discover_targets(goal)
    decision = choose_best_target(discovered)
    decision["source"] = "discovered_targets"
    decision["candidate_count"] = len(discovered)
    return decision.get("target", ""), decision

def create_patch_plan(goal: str, target: str | list[str] | None = None, reason: str = "", priority: str = "medium") -> dict:
    target_path, target_decision = _normalize_target(goal, target)

    if not target_path:
        return {
            "summary": f"{goal} | target=none | reason=no_discovered_target | priority={priority} | strategy=skip",
            "strategy": "skip",
            "strategy_reason": "no_target_available",
            "cooldown": False,
            "target_score": {},
            "target_decision": target_decision,
            "simulation": {"ok": False, "reason": "no_target"},
            "changes": []
        }

    strategy_info = choose_strategy_for_target(target_path)
    strategy = strategy_info["strategy"]

    if target_path.endswith("traffic_engine.py"):
        content = _traffic_engine_content(strategy)
    else:
        content = _generic_content(target_path, strategy)

    simulation = simulate_patch(target_path, content)
    if not simulation.get("ok"):
        strategy = "stabilize"
        if target_path.endswith("traffic_engine.py"):
            content = _traffic_engine_content(strategy)
        else:
            content = _generic_content(target_path, strategy)
        simulation = simulate_patch(target_path, content)

    target_score = score_target(target_path)

    return {
        "summary": f"{goal} | target={target_path} | reason={reason} | priority={priority} | strategy={strategy}",
        "strategy": strategy,
        "strategy_reason": strategy_info.get("reason", ""),
        "cooldown": strategy_info.get("cooldown", False),
        "target_score": target_score,
        "target_decision": target_decision,
        "simulation": simulation,
        "changes": [
            {
                "file": target_path,
                "content": content
            }
        ]
    }
