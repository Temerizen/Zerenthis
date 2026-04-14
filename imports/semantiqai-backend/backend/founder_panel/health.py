from .registry import discover_modules

def health_summary():
    modules = discover_modules()
    return {
        "status": "operational",
        "module_count": len(modules),
        "modules": modules,
        "alerts": [],
        "recommendation": "Continue installing remaining hardening and UI sweeps before public launch."
    }
