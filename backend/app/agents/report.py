from pathlib import Path
from backend.platform.registry import MODULE_REGISTRY
from backend.platform.paths import ROOT_DIR

def generate_cleanup_report():
    backend = ROOT_DIR / "backend"
    frontend = ROOT_DIR / "frontend"

    report = {
        "registry_count": len(MODULE_REGISTRY),
        "module_names": [m["name"] for m in MODULE_REGISTRY],
        "checks": {
            "backend_exists": backend.exists(),
            "frontend_exists": frontend.exists(),
            "server_exists": (backend / "server.py").exists(),
            "wsgi_exists": (backend / "wsgi.py").exists(),
            "frontend_app_exists": (frontend / "src" / "App.jsx").exists(),
            "frontend_api_exists": (frontend / "src" / "config" / "api.js").exists()
        },
        "warnings": []
    }

    if len(report["module_names"]) != len(set(report["module_names"])):
        report["warnings"].append("Duplicate module names detected in registry.")

    missing = [k for k, v in report["checks"].items() if not v]
    for item in missing:
        report["warnings"].append(f"Missing expected artifact: {item}")

    return report

