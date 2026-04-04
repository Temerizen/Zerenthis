from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from importlib import import_module
from datetime import datetime, timezone
from typing import List, Dict, Any
from pydantic import BaseModel
import json
import os
from threading import Lock
from uuid import uuid4

APP_TITLE = "Zerenthis Stabilized Core"
APP_VERSION = "12.0"

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
OUTPUT_DIR = DATA_DIR / "outputs"
JOB_FILE = DATA_DIR / "jobs.json"

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

ROUTER_MODULES: List[str] = []

_loaded_routes: List[Dict[str, Any]] = []
_startup_errors: List[Dict[str, str]] = []
_job_lock = Lock()
_jobs: Dict[str, Dict[str, Any]] = {}

class ProductPackRequest(BaseModel):
    topic: str = ""
    niche: str = ""
    tone: str = ""
    buyer: str = ""
    promise: str = ""
    bonus: str = ""
    notes: str = ""

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _load_jobs() -> None:
    global _jobs
    try:
        if JOB_FILE.exists():
            data = json.loads(JOB_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                _jobs = data
    except Exception:
        _jobs = {}

def _save_jobs() -> None:
    tmp = JOB_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(_jobs, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(JOB_FILE)

def _set_job(job_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    with _job_lock:
        current = _jobs.get(job_id, {})
        current.update(patch)
        _jobs[job_id] = current
        _save_jobs()
        return current

def _safe_include(module_name: str) -> None:
    global _loaded_routes, _startup_errors
    try:
        module = import_module(module_name)
        router = getattr(module, "router", None)
        if router is None:
            _startup_errors.append({"module": module_name, "error": "router attribute not found"})
            return
        app.include_router(router)
        _loaded_routes.append({"module": module_name, "status": "loaded"})
    except Exception as e:
        _startup_errors.append({"module": module_name, "error": str(e)})

for _module_name in ROUTER_MODULES:
    _safe_include(_module_name)

@app.on_event("startup")
def _startup() -> None:
    _load_jobs()

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
        "status": "ok",
        "name": APP_TITLE,
        "version": APP_VERSION,
        "time": _now(),
        "loaded_routes": len(_loaded_routes),
        "startup_errors": len(_startup_errors),
        "jobs": len(_jobs)
    }

@app.get("/api/system/routes")
def system_routes():
    return {
        "status": "ok",
        "time": _now(),
        "loaded": _loaded_routes,
        "startup_errors": _startup_errors
    }

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
        "startup_errors_count": len(_startup_errors),
        "jobs_count": len(_jobs)
    }

@app.post("/api/product-pack")
def create_product_pack(payload: ProductPackRequest, background_tasks: BackgroundTasks):
    job_id = uuid4().hex
    payload_dict = payload.model_dump()
    _set_job(job_id, {
        "job_id": job_id,
        "kind": "product",
        "status": "queued",
        "created_at": _now(),
        "payload": payload_dict,
        "error": None,
        "result": None,
        "file_name": None,
        "file_url": None,
    })

    def worker() -> None:
        try:
            _set_job(job_id, {"status": "running", "started_at": _now()})
            from backend.Engine.product_engine import build_product_pack
            result = build_product_pack(**payload_dict)
            file_name = Path(result.get("file_name", "")).name or None
            file_url = f"/api/file/{file_name}" if file_name else result.get("file_url")
            _set_job(job_id, {
                "status": "completed",
                "finished_at": _now(),
                "result": result,
                "file_name": file_name,
                "file_url": file_url,
            })
        except Exception as e:
            _set_job(job_id, {
                "status": "failed",
                "finished_at": _now(),
                "error": str(e),
            })

    background_tasks.add_task(worker)
    return {"ok": True, "job_id": job_id, "status": "queued"}

@app.get("/api/job/{job_id}")
def get_job(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/api/jobs")
def list_jobs():
    items = list(_jobs.values())
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return items

@app.get("/api/file/{name:path}")
def get_file(name: str):
    safe_name = Path(name).name
    candidates = [
        OUTPUT_DIR / safe_name,
        BASE_DIR / "backend" / "data" / "outputs" / safe_name,
        BASE_DIR / "backend" / "outputs" / safe_name,
    ]
    for target in candidates:
        if target.exists() and target.is_file():
            return FileResponse(str(target), filename=safe_name)
    raise HTTPException(status_code=404, detail="file not found")

