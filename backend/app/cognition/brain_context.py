import json
import os
from typing import Any, Dict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))

REFLECTION_PATH = os.path.join(ROOT_DIR, "backend", "data", "autonomy", "reflection_summary.json")
GOAL_PATH = os.path.join(ROOT_DIR, "backend", "data", "autonomy", "goal_state.json")

def _safe_load(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception as e:
        return {"load_error": str(e), "path": path}

def load_brain_context() -> Dict[str, Any]:
    reflection = _safe_load(REFLECTION_PATH)
    goal_state = _safe_load(GOAL_PATH)
    return {
        "reflection": reflection,
        "goal_state": goal_state,
    }
