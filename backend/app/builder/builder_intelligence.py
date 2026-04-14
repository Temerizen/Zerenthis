import difflib
from typing import Dict

BLOCKED_PATHS = ["site-packages","venv","__pycache__"]

MAX_CONTENT_CHANGE = 0.2  # ðŸ”¥ VERY STRICT


def is_risky(file_path: str) -> bool:
    return any(bad in file_path.lower() for bad in BLOCKED_PATHS)


def content_change_ratio(old: str, new: str) -> float:
    return 1 - difflib.SequenceMatcher(None, old, new).ratio()


def analyze_change(file_path: str, old_code: str, new_code: str) -> Dict:
    if is_risky(file_path):
        return {"status": "blocked", "reason": "risky_path"}

    content_ratio = content_change_ratio(old_code, new_code)

    print("CONTENT RATIO:", content_ratio)

    # ðŸ”¥ HARD BLOCK â€” ANY MAJOR CHANGE
    if content_ratio > MAX_CONTENT_CHANGE:
        return {
            "status": "rejected",
            "reason": "content_changed_too_much",
            "value": content_ratio
        }

    return {
        "status": "approved",
        "content_ratio": content_ratio
    }

