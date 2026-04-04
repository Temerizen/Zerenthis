from backend.platform.registry import MODULE_REGISTRY

def get_module_map():
    return [
        {
            "name": m["name"],
            "group": m.get("group", "general"),
            "route": m.get("route", f"/{m['name']}")
        }
        for m in MODULE_REGISTRY
    ]
