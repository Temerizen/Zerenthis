def is_valid_target(target: str) -> bool:
    if not isinstance(target, str):
        return False
    if target == "assets":
        return False
    if "/" not in target:
        return False
    if not target.endswith(".py"):
        return False
    return True
