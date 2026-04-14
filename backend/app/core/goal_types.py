def classify_goal(goal_id: str) -> str:
    goal_id = str(goal_id or "").lower()

    # Expansion first so initiative-like goals do not get swallowed by recovery
    if any(k in goal_id for k in ["initiate", "expand", "create", "explore", "advance", "discover"]):
        return "expansion"
    if any(k in goal_id for k in ["improve", "optimize", "enhance", "refine", "upgrade"]):
        return "optimization"
    if any(k in goal_id for k in ["recover", "failure", "fail", "error", "incident"]):
        return "recovery"
    if any(k in goal_id for k in ["fix", "reduce", "stabilize", "repair", "resolve"]):
        return "maintenance"

    return "maintenance"
