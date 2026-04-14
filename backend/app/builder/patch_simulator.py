from __future__ import annotations
from pathlib import Path

RESTRICTED_PARTS = ("venv", "__pycache__", ".git", "node_modules")

def simulate_patch(target_path: str, content: str) -> dict:
    normalized = str(target_path).replace("\\", "/").strip()

    if not normalized:
        return {"ok": False, "reason": "empty_target"}

    if any(part in normalized for part in RESTRICTED_PARTS):
        return {"ok": False, "reason": "restricted_target"}

    if not normalized.endswith(".py"):
        return {"ok": False, "reason": "non_python_target"}

    if not content or len(content.strip()) < 20:
        return {"ok": False, "reason": "empty_or_too_small"}

    if "def run(" not in content:
        return {"ok": False, "reason": "missing_run_function"}

    path = Path(normalized)
    if path.exists():
        try:
            existing = path.read_text(encoding="utf-8")
            if existing == content:
                return {"ok": False, "reason": "no_change"}
        except Exception:
            pass

    return {"ok": True, "reason": "passed"}
