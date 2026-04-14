from __future__ import annotations

from typing import Any

LOW = "low"
MEDIUM = "medium"
HIGH = "high"

HIGH_RISK_TOKENS = {
    "auth",
    "billing",
    "payment",
    "secret",
    ".env",
    "deploy",
    "railway",
    "vercel",
    "jwt",
    "login",
    "session",
    "token",
}

MEDIUM_RISK_TOKENS = {
    "main.py",
    "routes.py",
    "video_engine.py",
    "product_engine.py",
    "api",
    "cors",
}

def score_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    steps = proposal.get("steps", [])
    reasons: list[str] = []
    risk = LOW

    for step in steps:
        action = str(step.get("action", "")).lower()
        path = str(step.get("path", "")).lower()

        if action == "delete_file":
            risk = HIGH
            reasons.append(f"delete action on {path}")

        if any(tok in path for tok in HIGH_RISK_TOKENS):
            risk = HIGH
            reasons.append(f"high-risk path: {path}")
        elif any(tok in path for tok in MEDIUM_RISK_TOKENS):
            if risk != HIGH:
                risk = MEDIUM
            reasons.append(f"medium-risk path: {path}")

        if action == "create_file" and risk == LOW:
            reasons.append(f"safe create: {path}")
        if action == "edit_file" and risk == LOW:
            reasons.append(f"safe edit: {path}")

    return {
        "risk": risk,
        "reasons": reasons,
    }

