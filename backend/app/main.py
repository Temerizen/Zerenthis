from __future__ import annotations

import os
import sys
import json
from pathlib import Path
from collections import Counter
from self_improver.outcome_engine import log_result, suggest_next_move

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"

if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from self_improver.routes import router as self_router
from empire.routes import router as empire_router
from Engine.jobs import create_job, get_job
from Engine.product_engine import build_product_batch, build_product_pack
from Engine.video_engine import build_shorts_batch, build_shorts_video, build_youtube_pack

load_dotenv()

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = BACKEND_DIR / "data"
OUTPUT_DIR = DATA_DIR / "outputs"
SELF_DIR = DATA_DIR / "self_improver"
LEADS_DIR = DATA_DIR / "leads"
LEADS_FILE = LEADS_DIR / "intake_log.json"
EMPIRE_DIR = DATA_DIR / "empire"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SELF_DIR.mkdir(parents=True, exist_ok=True)
LEADS_DIR.mkdir(parents=True, exist_ok=True)
EMPIRE_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Zerenthis Automation Core")
app.include_router(self_router)
app.include_router(empire_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=200)
    niche: str = Field(default="Make Money Online")
    tone: str = Field(default="Premium")
    buyer: str = Field(default="Beginners starting from zero")
    promise: str = Field(default="")
    bonus: str = Field(default="")
    notes: str = Field(default="")
    duration_seconds: int = Field(default=35, ge=10, le=90)

class BatchRequest(GenerateRequest):
    count: int = Field(default=3, ge=1, le=10)

def get_base_url(request: Request | None = None) -> str:
    env_url = (os.getenv("PUBLIC_BASE_URL") or os.getenv("BASE_URL") or "").strip().rstrip("/")
    if env_url:
        return env_url
    if request is not None:
        return str(request.base_url).rstrip("/")
    return ""

def _load_json_list(path: Path):
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

@app.get("/")
def root():
    return {
        "status": "Zerenthis Automation Core Live",
        "service": "Zerenthis Automation Core",
        "docs": "/docs",
        "health": "/health",
        "gallery": "/api/gallery",
        "self_improver": "/api/self-improver/health",
        "empire": "/api/empire/state",
        "founder_metrics": "/api/founder/magic",
    }

@app.get("/health")
def health():
    files = [p for p in OUTPUT_DIR.iterdir() if p.is_file()]
    recent = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:5]
    proposals = _load_json_list(SELF_DIR / "proposals.json")
    execution_log = _load_json_list(SELF_DIR / "execution_log.json")
    empire_state = {}
    try:
        empire_state = json.loads((EMPIRE_DIR / "state.json").read_text(encoding="utf-8"))
    except Exception:
        empire_state = {}

    return {
        "ok": True,
        "service": "Zerenthis Automation Core",
        "outputs_dir": str(OUTPUT_DIR),
        "outputs_exists": OUTPUT_DIR.exists(),
        "output_count": len(files),
        "recent_outputs": [p.name for p in recent],
        "self_improver_records": len(proposals),
        "self_improver_executions": len(execution_log),
        "empire_mode": True,
        "compound_score": empire_state.get("compound_score", 0),
    }

@app.get("/api/founder/magic")
def founder_magic():
    files = [p for p in OUTPUT_DIR.iterdir() if p.is_file()]
    proposals = _load_json_list(SELF_DIR / "proposals.json")
    execution_log = _load_json_list(SELF_DIR / "execution_log.json")
    leads = _load_json_list(LEADS_FILE)
    empire_state = {}
    empire_reflections = []
    empire_offers = []
    try:
        empire_state = json.loads((EMPIRE_DIR / "state.json").read_text(encoding="utf-8"))
    except Exception:
        empire_state = {}
    try:
        empire_reflections = json.loads((EMPIRE_DIR / "reflections.json").read_text(encoding="utf-8"))
    except Exception:
        empire_reflections = []
    try:
        empire_offers = json.loads((EMPIRE_DIR / "offers.json").read_text(encoding="utf-8"))
    except Exception:
        empire_offers = []

    status_counts = Counter(item.get("status", "unknown") for item in proposals)
    exec_counts = Counter(item.get("status", "unknown") for item in execution_log)
    recent_files = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:10]

    return {
        "ok": True,
        "engine_state": "empire-operator",
        "outputs": {
            "count": len(files),
            "recent": [p.name for p in recent_files],
        },
        "self_improver": {
            "proposals_total": len(proposals),
            "status_counts": dict(status_counts),
            "execution_counts": dict(exec_counts),
        },
        "leads": {
            "count": len(leads),
            "contactable": sum(1 for x in leads if x.get("customer_email")),
            "consented": sum(1 for x in leads if x.get("marketing_consent")),
        },
        "empire": {
            "cycles": empire_state.get("cycles", 0),
            "compound_score": empire_state.get("compound_score", 0),
            "focus": empire_state.get("focus", []),
            "last_actions": empire_state.get("last_actions", []),
            "top_offer": empire_offers[0]["title"] if empire_offers else None,
            "latest_reflection": empire_reflections[-1] if empire_reflections else None,
        },
    }

@app.post("/api/product-pack")
def product_pack(payload: GenerateRequest, request: Request):
    job_id = create_job(
        "product",
        payload.model_dump(),
        build_product_pack,
        topic=payload.topic,
        niche=payload.niche,
        tone=payload.tone,
        buyer=payload.buyer,
        promise=payload.promise,
        bonus=payload.bonus,
        notes=payload.notes,
        base_url=get_base_url(request),
    )
    return {"job_id": job_id, "status": "queued"}

@app.post("/api/shorts-pack")
def shorts_pack(payload: GenerateRequest, request: Request):
    job_id = create_job(
        "shorts",
        payload.model_dump(),
        build_shorts_video,
        topic=payload.topic,
        tone=payload.tone,
        promise=payload.promise,
        duration_seconds=payload.duration_seconds,
        base_url=get_base_url(request),
    )
    return {"job_id": job_id, "status": "queued"}

@app.post("/api/youtube-pack")
def youtube_pack(payload: GenerateRequest):
    return build_youtube_pack(
        topic=payload.topic,
        niche=payload.niche,
        tone=payload.tone,
        buyer=payload.buyer,
        promise=payload.promise,
        bonus=payload.bonus,
        notes=payload.notes,
    )

@app.post("/api/founder/product-batch")
def founder_product_batch(payload: BatchRequest, request: Request):
    job_id = create_job(
        "product_batch",
        payload.model_dump(),
        build_product_batch,
        topic=payload.topic,
        niche=payload.niche,
        tone=payload.tone,
        buyer=payload.buyer,
        promise=payload.promise,
        bonus=payload.bonus,
        notes=payload.notes,
        base_url=get_base_url(request),
        count=payload.count,
    )
    return {"job_id": job_id, "status": "queued"}

@app.post("/api/founder/shorts-batch")
def founder_shorts_batch(payload: BatchRequest, request: Request):
    job_id = create_job(
        "shorts_batch",
        payload.model_dump(),
        build_shorts_batch,
        topic=payload.topic,
        tone=payload.tone,
        promise=payload.promise,
        duration_seconds=payload.duration_seconds,
        base_url=get_base_url(request),
        count=payload.count,
    )
    return {"job_id": job_id, "status": "queued"}

@app.get("/api/job/{job_id}")
def job_status(job_id: str):
    data = get_job(job_id)
    if data.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Job not found")
    return data

@app.get("/api/file/{name}")
def serve_file(name: str):
    if "/" in name or "\\" in name:
        raise HTTPException(status_code=400, detail="Invalid file name")

    path = OUTPUT_DIR / name
    if not path.exists():
        raise HTTPException(status_code=404, detail="File missing")

    media_type = None
    if path.suffix.lower() == ".pdf":
        media_type = "application/pdf"
    elif path.suffix.lower() == ".mp4":
        media_type = "video/mp4"
    elif path.suffix.lower() == ".png":
        media_type = "image/png"

    return FileResponse(path, media_type=media_type, filename=path.name)

@app.get("/api/gallery")
def gallery():
    items = []
    for path in sorted(OUTPUT_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if not path.is_file():
            continue
        items.append(
            {
                "name": path.name,
                "size_bytes": path.stat().st_size,
                "modified_ts": path.stat().st_mtime,
                "url": f"/api/file/{path.name}",
                "extension": path.suffix.lower(),
            }
        )
    return {"items": items[:200]}
@app.post("/api/self/log")
def log_performance(data: dict):
    log_result(data)
    return {"status": "logged"}

@app.get("/api/self/suggest")
def suggest():
    return suggest_next_move()

