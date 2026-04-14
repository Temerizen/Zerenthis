from backend.app.builder.policy_engine import path_status, load_policy
from backend.app.builder.apply_engine import apply_patch_plan

def builder_guardrails_status() -> dict:
    return {
        "status": "ok",
        "policy": load_policy()
    }

def builder_probe_path(path: str) -> dict:
    return {
        "path": path,
        "status": path_status(path)
    }

