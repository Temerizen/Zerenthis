from __future__ import annotations

from typing import Any

def build_mitigation_notes(proposal: dict[str, Any]) -> dict[str, Any]:
    steps = proposal.get("steps", [])
    notes: list[str] = []

    for step in steps:
        action = str(step.get("action", ""))
        path = str(step.get("path", ""))

        if action == "delete_file":
            notes.append(f"Delete action kept for approval: {path}")
        elif any(tok in path.lower() for tok in ["auth", "billing", "payment", ".env", "deploy", "railway", "vercel", "jwt", "token", "secret"]):
            notes.append(f"Sensitive path kept for approval: {path}")
        else:
            notes.append(f"Prepared safely: {path}")

    return {
        "mitigation_notes": notes
    }

