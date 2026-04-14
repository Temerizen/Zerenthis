from typing import Dict, Any

def run(context: Dict[str, Any] | None = None):
    context = context or {}

    override_goal = context.get("override_goal")
    if override_goal:
        return {
            "status": "goal_updated",
            "active_goal": override_goal,
            "changed": True
        }

    decision = context.get("decision", {})
    mode = decision.get("mode", "balanced")

    if mode == "explore":
        goal = "expand_capability"
    elif mode == "persist":
        goal = "reinforce_path"
    elif mode == "stabilize":
        goal = "reduce_variance"
    else:
        goal = "balanced_progression"

    return {
        "status": "goal_updated",
        "active_goal": goal,
        "changed": True
    }
