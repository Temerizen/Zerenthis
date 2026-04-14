def should_build(goal):
    gid = str(goal.get("id") or "").lower()

    if "recovery" in gid:
        return True, "stabilization_build"

    if "explore" in gid:
        return True, "exploration_build"

    if "improve" in gid:
        return True, "optimization_build"

    return False, None
