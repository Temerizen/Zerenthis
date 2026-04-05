import os
from backend.app.core.registry_engine import get_registry, update_module

OUTPUT_ROOT = os.path.join("backend", "outputs")

def founder_summary():
    registry = get_registry()
    update_module("founder", last_output="founder_summary")
    return registry

def founder_recent_outputs(limit=25):
    results = []
    if os.path.isdir(OUTPUT_ROOT):
        for root, dirs, files in os.walk(OUTPUT_ROOT):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, OUTPUT_ROOT).replace("\\", "/")
                results.append({
                    "file_name": rel,
                    "file_url": f"/api/file/{rel}",
                    "modified": os.path.getmtime(full)
                })
    results = sorted(results, key=lambda x: x["modified"], reverse=True)[:limit]
    update_module("founder", last_output=f"recent_outputs:{len(results)}")
    return {
        "status": "ok",
        "count": len(results),
        "outputs": results
    }

def founder_module_status():
    registry = get_registry()
    modules = registry.get("modules", {})
    update_module("founder", last_output="module_status")
    return {
        "status": "ok",
        "modules": modules
    }
