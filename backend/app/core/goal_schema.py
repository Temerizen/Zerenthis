def enforce_goal_schema(goal):
    if isinstance(goal, str):
        return {
            "id": goal,
            "type": "generated",
            "priority": 0.5,
            "reason": goal,
            "goal_type": "expansion",
            "metadata": {}
        }

    if not isinstance(goal, dict):
        return None

    return {
        "id": goal.get("id") or goal.get("objective") or "unknown_goal",
        "type": goal.get("type", "generated"),
        "priority": float(goal.get("priority", 0.5)),
        "reason": goal.get("reason") or goal.get("objective"),
        "goal_type": goal.get("goal_type", "expansion"),
        "metadata": goal.get("metadata", {})
    }
