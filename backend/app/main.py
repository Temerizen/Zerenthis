from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from importlib import import_module
from datetime import datetime, timezone
from typing import List, Dict, Any
import os

APP_TITLE = "Zerenthis Stabilized Core"
APP_VERSION = "10.0"

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROUTER_MODULES: List[str] = [
    "backend.app.adaptive_brain",
 "backend.app.auto_engine",
    "backend.app.autonomy",
    "backend.app.failsafe",
    "backend.app.command_center",
    "backend.app.knowledge",
    "backend.app.workflow_builder",
    "backend.app.browser_operator",
    "backend.app.inbox",
    "backend.app.live_mode",
    "backend.app.evals",
    "backend.app.vision_hardening",
    "backend.app.vision",
    "backend.app.monetization",
    "backend.app.intelligence",
    "backend.app.system_hardening",
    "backend.app.winner_cycle",
    "backend.app.control_tower",
    "backend.app.money_sweep",
    "backend.app.output_routes",
    "backend.app.expansion_routes",
    "backend.app.orchestrator_routes",
    "backend.app.learning_routes",
    "backend.app.decision_routes",
    "backend.app.autopilot_routes",
    "backend.app.money_routes",
    "backend.app.founder",
    "backend.app.limit_lock",
    "backend.app.evo_routes",
]

_loaded_routes: List[Dict[str, Any]] = []
_startup_errors: List[Dict[str, str]] = []

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _safe_include(module_name: str) -> None:
    global _loaded_routes, _startup_errors
    try:
        module = import_module(module_name)
        router = getattr(module, "router", None)
        if router is None:
            _startup_errors.append({
                "module": module_name,
                "error": "router attribute not found"
            })
            return
        app.include_router(router)
        _loaded_routes.append({
            "module": module_name,
            "status": "loaded"
        })
    except Exception as e:
        _startup_errors.append({
            "module": module_name,
            "error": str(e)
        })

for _module_name in ROUTER_MODULES:
    _safe_include(_module_name)

@app.get("/")
def root():
    return {
        "status": "ok",
        "name": APP_TITLE,
        "version": APP_VERSION,
        "time": _now(),
        "message": "Zerenthis stabilized core is running"
    }

@app.get("/health")
def health():
    return {
        "ok": True,
        "name": APP_TITLE,
        "version": APP_VERSION,
        "time": _now(),
        "loaded_routes": len(_loaded_routes),
        "startup_errors": len(_startup_errors)
    }

@app.get("/api/system/routes")
def system_routes():
    return {
        "status": "ok",
        "time": _now(),
        "loaded": _loaded_routes,
        "startup_errors": _startup_errors
    }

@app.get("/api/file/{name:path}")
def get_file(name: str):
    safe_name = Path(name).name
    target = OUTPUT_DIR / safe_name
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(str(target), filename=safe_name)

@app.get("/api/system/info")
def system_info():
    return {
        "status": "ok",
        "base_dir": str(BASE_DIR),
        "data_dir": str(DATA_DIR),
        "output_dir": str(OUTPUT_DIR),
        "python_env_openai_model": os.getenv("OPENAI_MODEL", "").strip(),
        "python_env_has_openai_key": bool(os.getenv("OPENAI_API_KEY", "").strip()),
        "loaded_routes_count": len(_loaded_routes),
        "startup_errors_count": len(_startup_errors)
    }



