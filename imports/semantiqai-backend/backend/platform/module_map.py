from backend.platform.registry import MODULE_REGISTRY

def get_module_map():
    seen = set()
    items = []

    for m in MODULE_REGISTRY:
        key = m["name"]
        if key in seen:
            continue
        seen.add(key)
        items.append({
            "name": m["name"],
            "group": m.get("group", "general"),
            "route": m.get("route", f"/{m['name']}"),
            "blueprint": m.get("blueprint_name", m["name"])
        })

    return items
