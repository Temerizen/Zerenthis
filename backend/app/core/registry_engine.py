import json
import os
from datetime import datetime, timezone

DATA_DIR = os.path.join("backend", "data")
REGISTRY_PATH = os.path.join(DATA_DIR, "module_registry.json")

DEFAULT_REGISTRY = {
    "generated_at": None,
    "modules": {
        "core": {"status": "active", "last_run": None, "last_output": None, "last_error": None},
        "money": {"status": "active", "last_run": None, "last_output": None, "last_error": None},
        "content": {"status": "active", "last_run": None, "last_output": None, "last_error": None},
        "school": {"status": "active", "last_run": None, "last_output": None, "last_error": None},
        "research": {"status": "active", "last_run": None, "last_output": None, "last_error": None},
        "cognitive": {"status": "active", "last_run": None, "last_output": None, "last_error": None},
        "genius": {"status": "active", "last_run": None, "last_output": None, "last_error": None},
        "founder": {"status": "active", "last_run": None, "last_output": None, "last_error": None}
    }
}

def _utc_now():
    return datetime.now(timezone.utc).isoformat()

def _ensure():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_REGISTRY, f, indent=2)

def load_registry():
    _ensure()
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_registry(registry):
    registry["generated_at"] = _utc_now()
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

def update_module(module_name, last_output=None, last_error=None, status="active"):
    registry = load_registry()
    modules = registry.setdefault("modules", {})
    module = modules.setdefault(module_name, {"status": "active", "last_run": None, "last_output": None, "last_error": None})
    module["status"] = status
    module["last_run"] = _utc_now()
    if last_output is not None:
        module["last_output"] = last_output
    if last_error is not None:
        module["last_error"] = last_error
    save_registry(registry)
    return registry

def get_registry():
    return load_registry()

