from __future__ import annotations

from typing import Any

SAFE_AUTO_PATH_PREFIXES = (
    "backend/app/",
    "frontend/",
)

HARD_BLOCK_TOKENS = (
    ".env",
    ".git",
    "node_modules",
    "venv",
    "backend/data",
    "auth",
    "billing",
    "stripe",
    "railway",
    "vercel",
    "deploy",
    "secret",
    "token",
    "password",
    "key",
)

CORE_BLOCK_PATHS = {
    "backend/self_improver/engine.py",
    "backend/self_improver/worker.py",
    "backend/self_improver/autopilot.py",
    "backend/self_improver/policy.py",
    "backend/self_improver/brain/ai_brain.py",
}

def _norm(path: str) -> str:
    return str(path).replace("\\", "/").strip().lower()

def classify_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    steps = proposal.get("steps", []) or []
    title = str(proposal.get("title", "")).strip()
    risk = 0
    reasons: list[str] = []

    if not steps:
        return {
            "tier": "blocked",
            "risk_score": 999,
            "reasons": ["No steps provided"],
            "auto_approve": False,
            "title": title,
        }

    if len(steps) >= 4:
        risk += 3
        reasons.append("Many steps")

    touched_paths: list[str] = []
    actions = []

    for step in steps:
        action = str(step.get("action", "")).strip()
        path = _norm(step.get("path", ""))
        actions.append(action)
        touched_paths.append(path)

        if not path:
            return {
                "tier": "blocked",
                "risk_score": 999,
                "reasons": ["Missing path"],
                "auto_approve": False,
                "title": title,
            }

        if path in CORE_BLOCK_PATHS:
            return {
                "tier": "blocked",
                "risk_score": 999,
                "reasons": [f"Touches protected core path: {path}"],
                "auto_approve": False,
                "title": title,
            }

        if any(token in path for token in HARD_BLOCK_TOKENS):
            return {
                "tier": "blocked",
                "risk_score": 999,
                "reasons": [f"Touches blocked area: {path}"],
                "auto_approve": False,
                "title": title,
            }

        if path.endswith("product_engine.py") or path.endswith("video_engine.py"):
            risk += 3
            reasons.append(f"Core generator file: {path}")

        if not path.startswith(SAFE_AUTO_PATH_PREFIXES) and not path.endswith("product_engine.py") and not path.endswith("video_engine.py"):
            risk += 2
            reasons.append(f"Non-standard path: {path}")

        if action == "delete_file":
            risk += 5
            reasons.append(f"Deletes file: {path}")

        elif action == "edit_file":
            find = str(step.get("find", ""))
            replace = str(step.get("replace", ""))
            if len(find) > 2000 or len(replace) > 5000:
                risk += 3
                reasons.append(f"Large edit: {path}")
            if path.endswith("main.py"):
                risk += 2
                reasons.append("Touches main.py")

        elif action == "create_file":
            content = str(step.get("content", ""))
            if len(content) > 5000:
                risk += 2
                reasons.append(f"Large new file: {path}")

        else:
            return {
                "tier": "blocked",
                "risk_score": 999,
                "reasons": [f"Unsupported action: {action}"],
                "auto_approve": False,
                "title": title,
            }

    unique_paths = set(touched_paths)
    if len(unique_paths) >= 3:
        risk += 2
        reasons.append("Touches many files")

    if "delete_file" in actions:
        tier = "high"
    elif risk <= 1:
        tier = "low"
    elif risk <= 4:
        tier = "medium"
    else:
        tier = "high"

    return {
        "tier": tier,
        "risk_score": risk,
        "reasons": reasons or ["Low-risk change"],
        "auto_approve": tier == "low",
        "title": title,
        "paths": sorted(unique_paths),
    }

