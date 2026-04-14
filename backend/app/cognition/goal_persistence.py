import json
import os
import time
from typing import Any, Dict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))

GOAL_PATH = os.path.join(ROOT_DIR, "backend", "data", "autonomy", "goal_state.json")
REFLECTION_PATH = os.path.join(ROOT_DIR, "backend", "data", "autonomy", "reflection_summary.json")

DEFAULT_GOAL_STATE = {
    "identity": "Zerenthis",
    "primary_goal": "Maintain stable autonomous operation and prepare for safe expansion",
    "active_mode": "stability_first",
    "status": "active",
    "priority": "high",
    "created_at": None,
    "updated_at": None,
    "last_reflection_assessment": None,
    "last_reflection_recommendation": None,
    "history": []
}

def _safe_clone(default: Dict[str, Any]) -> Dict[str, Any]:
    return json.loads(json.dumps(default))

def _safe_load(path: str, default: Dict[str, Any]) -> Dict[str, Any]:
    if not os.path.exists(path):
        print(f"[WARN] Missing file: {path}")
        return _safe_clone(default)
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            print(f"[DEBUG] Loaded {path}")
            return data
    except Exception as e:
        print(f"[ERROR] Failed to load {path}: {e}")
        return _safe_clone(default)

def _safe_save(path: str, data: Dict[str, Any]) -> Dict[str, Any]:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return data

def run_goal_persistence() -> Dict[str, Any]:
    now = time.time()
    goal_state = _safe_load(GOAL_PATH, DEFAULT_GOAL_STATE)

    if goal_state.get("created_at") is None:
        goal_state["created_at"] = now

    reflection = _safe_load(REFLECTION_PATH, {})

    print("[DEBUG] Reflection content:", reflection)

    assessment = reflection.get("assessment")
    recommendation = reflection.get("next_recommendation")

    goal_state["updated_at"] = now
    goal_state["last_reflection_assessment"] = assessment
    goal_state["last_reflection_recommendation"] = recommendation

    if assessment == "stable_persistent_autonomy_confirmed":
        goal_state["active_mode"] = "goal_persistence"
        goal_state["primary_goal"] = "Maintain stable autonomous operation while expanding safe self-model and goal continuity"
        goal_state["status"] = "active"
        goal_state["priority"] = "high"
    elif assessment == "stable_autonomy_observed":
        goal_state["active_mode"] = "stability_validation"
        goal_state["primary_goal"] = "Increase autonomous runtime and validate sustained stability"
        goal_state["status"] = "active"
        goal_state["priority"] = "high"
    elif assessment == "mostly_stable_minor_faults":
        goal_state["active_mode"] = "repair"
        goal_state["primary_goal"] = "Fix minor faults before expanding intelligence layers"
        goal_state["status"] = "guarded"
        goal_state["priority"] = "critical"
    else:
        goal_state["active_mode"] = "stabilization"
        goal_state["primary_goal"] = "Stabilize the autonomous core before any expansion"
        goal_state["status"] = "guarded"
        goal_state["priority"] = "critical"

    goal_state["history"].append({
        "timestamp": now,
        "assessment": assessment,
        "recommendation": recommendation,
        "mode": goal_state["active_mode"],
        "goal": goal_state["primary_goal"],
        "status": goal_state["status"],
        "priority": goal_state["priority"]
    })

    goal_state["history"] = goal_state["history"][-25:]
    _safe_save(GOAL_PATH, goal_state)

    return {
        "status": "ok",
        "goal_state": goal_state
    }

if __name__ == "__main__":
    result = run_goal_persistence()
    print(json.dumps(result, indent=2))
