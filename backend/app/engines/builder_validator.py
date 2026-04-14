import json, os, time

PLAN_PATH = "backend/outputs/builder_plan.json"
VALIDATION_PATH = "backend/outputs/builder_validation.json"

ALLOWED_PATCH_TYPES = {
    "increase_reality_feedback",
    "improve_structure_clarity",
    "general_companion_improvement"
}

def load_json(path, default=None):
    default = {} if default is None else default
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def validate_builder_plan(path=PLAN_PATH):
    plan = load_json(path, {})
    issues = []
    warnings = []

    if not plan:
        issues.append("missing_plan")
    else:
        if plan.get("status") != "planned":
            issues.append("plan_status_not_planned")

        target = plan.get("target")
        if not target:
            issues.append("missing_target")
        else:
            if not str(target).startswith("backend/"):
                issues.append("target_outside_backend")
            if str(target).endswith("main.py"):
                warnings.append("target_is_main_py")
            if "__pycache__" in str(target):
                issues.append("target_points_to_cache")

        patch_type = plan.get("patch_type")
        if patch_type not in ALLOWED_PATCH_TYPES:
            issues.append("patch_type_not_allowed")

        proposed_changes = plan.get("proposed_changes", [])
        if not isinstance(proposed_changes, list) or not proposed_changes:
            issues.append("missing_proposed_changes")

        if plan.get("safe_mode") is not True:
            issues.append("safe_mode_not_enabled")

    validated = len(issues) == 0
    safe_to_apply = validated and "target_is_main_py" not in warnings

    result = {
        "status": "validated" if validated else "rejected",
        "validated": validated,
        "safe_to_apply": safe_to_apply,
        "issues": issues,
        "warnings": warnings,
        "checked_path": path,
        "timestamp": time.time()
    }

    save_json(VALIDATION_PATH, result)
    return result
