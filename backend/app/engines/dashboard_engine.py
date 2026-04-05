from backend.app.core.registry_engine import get_registry
from backend.app.engines.founder_engine import founder_recent_outputs

def get_dashboard():
    registry = get_registry()
    outputs = founder_recent_outputs(limit=10)

    return {
        "status": "online",
        "modules": registry.get("modules", {}),
        "recent_outputs": outputs.get("outputs", []),
        "system": {
            "active": True,
            "mode": "autonomous",
            "version": "sweep5"
        }
    }
