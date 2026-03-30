from __future__ import annotations

from copy import deepcopy
from typing import Any

def decompose_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    proposal = deepcopy(proposal)
    steps = proposal.get("steps", [])

    safe_steps: list[dict[str, Any]] = []
    risky_steps: list[dict[str, Any]] = []

    for step in steps:
        path = str(step.get("path", "")).lower()
        action = str(step.get("action", "")).lower()

        if any(tok in path for tok in ["auth", "billing", "payment", ".env", "deploy", "railway", "vercel", "jwt", "token", "secret"]):
            risky_steps.append(step)
            continue

        if action == "delete_file":
            risky_steps.append(step)
            continue

        safe_steps.append(step)

    return {
        "original": proposal,
        "safe_proposal": {
            "title": f"{proposal.get('title', 'Proposal')} [safe-prep]",
            "reason": f"Safe preparation extracted from: {proposal.get('reason', '')}",
            "steps": safe_steps,
        } if safe_steps else None,
        "risky_remainder": {
            "title": f"{proposal.get('title', 'Proposal')} [approval-needed]",
            "reason": f"Risky remainder after safe preparation: {proposal.get('reason', '')}",
            "steps": risky_steps,
        } if risky_steps else None,
    }

