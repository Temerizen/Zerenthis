from __future__ import annotations
from pathlib import Path

ENGINE_ROOT = Path("backend/app/engines")

EXCLUDED_NAMES = {
    "__init__.py",
}

EXCLUDED_HINTS = (
    "__pycache__",
    "test",
    "spec",
)

def discover_targets(goal: str = "") -> list[str]:
    if not ENGINE_ROOT.exists():
        return []

    goal_text = (goal or "").lower().strip()
    candidates: list[str] = []

    for path in ENGINE_ROOT.glob("*.py"):
        name = path.name.lower()
        full = path.as_posix()

        if name in EXCLUDED_NAMES:
            continue
        if any(hint in name for hint in EXCLUDED_HINTS):
            continue

        candidates.append(full)

    # light goal-aware bias by ordering, scorer still decides final winner
    def sort_key(p: str) -> tuple[int, str]:
        n = Path(p).name.lower()

        if any(word in goal_text for word in ["money", "revenue", "sales", "profit", "monet"]):
            if "offer" in n: return (0, n)
            if "sales" in n: return (1, n)
            if "store" in n: return (2, n)
            if "traffic" in n: return (3, n)

        if any(word in goal_text for word in ["video", "content", "viral", "media"]):
            if "video" in n: return (0, n)
            if "traffic" in n: return (1, n)

        return (50, n)

    candidates.sort(key=sort_key)
    return candidates
