import json
from pathlib import Path

ACTIVE_GOAL_PATH = Path("backend/data/active_goal.json")

def safe_write_active_goal(data):
    # Only allow new structured format
    if not isinstance(data, dict):
        return

    if "active_goal" not in data:
        # BLOCK legacy overwrite
        return

    ACTIVE_GOAL_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
