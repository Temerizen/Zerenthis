from __future__ import annotations

import sys
from pathlib import Path
import os

# ✅ Fix import paths
sys.path.append(str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from urllib.parse import quote
from pydantic import BaseModel, Field, EmailStr, field_validator
import json

# ✅ Routers
from backend.self_improver.routes import router as self_router

# ✅ Engines
from Engine.jobs import create_job, get_job
from Engine.product_engine import build_product_batch, build_product_pack
from Engine.video_engine import build_shorts_batch, build_shorts_video, build_youtube_pack

# ✅ Paths
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
OUTPUT_DIR = BACKEND_DIR / "data" / "outputs"
LEADS_DIR = BACKEND_DIR / "data" / "leads"
LEADS_FILE = LEADS_DIR / "intake_log.json"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LEADS_DIR.mkdir(parents=True, exist_ok=True)

# ✅ Initialize app PROPERLY
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",") if o.strip()]

app = FastAPI(title="Zerenthis Automation Core")

# ✅ Register self-improver routes
app.include_router(self_router)

# ✅ Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS else ["*"],
    allow_credentials=False if "*" in ALLOWED_ORIGINS else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 📦 MODELS
# =========================

class GenerateRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=200)
    niche: str = Field(default="Make Money Online", max_length=120)
    tone: str = Field(default="Premium", max_length=60)
    buyer: str = Field(default="Beginners starting from zero", max_length=160)
    promise: str = Field(default="", max_length=200)
    bonus: str = Field(default="", max_length=200)
    notes: str = Field(default="", max_length=1000)
    duration_seconds: int = Field(default=35, ge=10, le=90)
    customer_name: str = Field(default="", max_length=120)
    customer_email: EmailStr | None = None
    marketing_consent: bool = False

    @field_validator("topic", "niche", "tone", "buyer", "promise", "bonus", "notes", "customer_name", mode="before")
    @classmethod
    def normalize_text(cls, value):
        if value is None:
            return ""
        if not isinstance(value, str):
            return value
        return " ".join(value.strip().split())

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, value: str):
        if len(value) < 3:
            raise ValueError("topic must be at least 3 characters")
        lowered = value.lower()
        blocked = ["test", "asdf", "qwerty", "lorem ipsum"]
        if lowered in blocked:
            raise ValueError("topic is too low-signal")
        return value


class BatchRequest(GenerateRequest):
    count: int = Field(default=3, ge=1, le=10)


# =========================
# 🧠 HELPERS
# =========================

def get_base_url() -> str:
    public_base = os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/")
    if public_base:
        return public_base
    return "http://localhost:8000"


def log_lead(source: str, payload: GenerateRequest, job_id: str | None = None) -> None:
    if not payload.customer_email and not payload.customer_name:
        return

    items = []
    if LEADS_FILE.exists():
        try:
            items = json.loads(LEADS_FILE.read_text(encoding="utf-8"))
            if not isinstance(items, list):
                items = []
        except Exception:
            items = []

    items.append({
        "source": source,
        "job_id": job_id,
        "topic": payload.topic,
        "niche": payload.niche,
        "customer_name": payload.customer_name,
        "customer_email": str(payload.customer_email) if payload.customer_email else "",
        "marketing_consent": payload.marketing_consent,
    })
    temp_file = LEADS_FILE.with_suffix(".tmp")
    temp_file.write_text(json.dumps(items, indent=2), encoding="utf-8")
    temp_file.replace(LEADS_FILE)


def get_lead_metrics() -> dict:
    items = []
    if LEADS_FILE.exists():
        try:
            loaded = json.loads(LEADS_FILE.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                items = loaded
        except Exception:
            items = []

    consented = sum(1 for item in items if item.get("marketing_consent"))
    with_email = sum(1 for item in items if item.get("customer_email"))
    by_source = {}
    for item in items:
        source = item.get("source", "unknown")
        by_source[source] = by_source.get(source, 0) + 1

    return {
        "total": len(items),
        "with_email": with_email,
        "marketing_consented": consented,
        "by_source": by_source,
    }


# =========================
# 🌐 CORE ROUTES
# =========================

@app.get("/")
def root():
    return {"status": "Zerenthis Automation Core Live"}


@app.get("/health")
def health():
    lead_metrics = get_lead_metrics()
    outputs = [p for p in OUTPUT_DIR.iterdir() if p.is_file()]
    latest_output_path = max(outputs, key=lambda p: p.stat().st_mtime) if outputs else None
    latest_output = latest_output_path.name if latest_output_path else None
    output_breakdown = {}
    for output in outputs:
        ext = output.suffix.lower() or "[no_ext]"
        output_breakdown[ext] = output_breakdown.get(ext, 0) + 1

    recent_outputs = sorted(outputs, key=lambda p: p.stat().st_mtime, reverse=True)[:5]
    recent_output_names = [p.name for p in recent_outputs]
    product_readiness = {
        "has_pdf_outputs": output_breakdown.get(".pdf", 0) > 0,
        "has_video_outputs": any(ext in output_breakdown for ext in [".mp4", ".mov"]),
        "lead_capture_active": LEADS_FILE.exists(),
        "has_public_base_url": bool(os.getenv("PUBLIC_BASE_URL", "").strip()),
        "has_consented_leads": lead_metrics["marketing_consented"] > 0,
    }

    return {
        "ok": True,
        "service": "Zerenthis Automation Core",
        "output_dir": str(OUTPUT_DIR),
        "output_count": len(outputs),
        "output_breakdown": output_breakdown,
        "lead_count": lead_metrics["total"],
        "lead_metrics": lead_metrics,
        "has_public_base_url": bool(os.getenv("PUBLIC_BASE_URL", "").strip()),
        "cors_origin_count": len(ALLOWED_ORIGINS) if ALLOWED_ORIGINS else 1,
        "latest_output": latest_output,
        "latest_output_size_bytes": latest_output_path.stat().st_size if latest_output_path else 0,
        "recent_outputs": recent_output_names,
        "product_readiness": product_readiness,
        "metrics_url": f"{get_base_url()}/api/metrics",
        "self_improver_url": f"{get_base_url()}/self/stats",
    }


@app.get("/api/catalog")
def catalog():
    return {
        "brand": "Zerenthis",
        "currency": "USD",
        "positioning": "AI-powered digital product and content generation",
        "products": [
            {
                "id": "product-pack",
                "name": "Execution Pack PDF",
                "category": "digital-product",
                "starting_price": 19,
                "deliverable": "pdf",
                "best_for": "lead capture and low-ticket monetization",
                "cta": "Generate a monetizable PDF pack"
            },
            {
                "id": "shorts-pack",
                "name": "Shorts Content Pack",
                "category": "content",
                "starting_price": 29,
                "deliverable": "video-assets",
                "best_for": "traffic generation and organic promotion"
            },
            {
                "id": "youtube-pack",
                "name": "YouTube Growth Pack",
                "category": "content-strategy",
                "starting_price": 49,
                "deliverable": "script-pack",
                "best_for": "authority building and upsells"
            }
        ]
    }


@app.get("/api/metrics")
def metrics():
    leads = []
    if LEADS_FILE.exists():
        try:
            loaded = json.loads(LEADS_FILE.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                leads = loaded
        except Exception:
            leads = []

    outputs = [p for p in OUTPUT_DIR.iterdir() if p.is_file()]
    by_source = {}
    consented = 0
    contactable = 0
    named = 0
    file_types = {}
    for output in outputs:
        suffix = output.suffix.lower() or "no_extension"
        file_types[suffix] = file_types.get(suffix, 0) + 1
    for item in leads:
        source = item.get("source", "unknown")
        by_source[source] = by_source.get(source, 0) + 1
        if item.get("marketing_consent"):
            consented += 1
        if item.get("customer_email"):
            contactable += 1
        if item.get("customer_name"):
            named += 1

    conversion_rate = round((len(leads) / len(outputs)) * 100, 2) if outputs else 0.0
    consent_rate = round((consented / len(leads)) * 100, 2) if leads else 0.0
    contact_rate = round((contactable / len(leads)) * 100, 2) if leads else 0.0
    named_rate = round((named / len(leads)) * 100, 2) if leads else 0.0

    latest_outputs = sorted(outputs, key=lambda p: p.stat().st_mtime, reverse=True)[:10]
    return {
        "ok": True,
        "service": "Zerenthis Automation Core",
        "lead_count": len(leads),
        "output_count": len(outputs),
        "conversion_rate": conversion_rate,
        "consented_lead_count": consented,
        "contactable_lead_count": contactable,
        "named_lead_count": named,
        "consent_rate": consent_rate,
        "contact_rate": contact_rate,
        "named_rate": named_rate,
        "leads_by_source": by_source,
        "outputs_by_type": file_types,
        "latest_outputs": [p.name for p in latest_outputs],
        "public_base_url": get_base_url(),
    }
    consent_rate = round((consented / len(leads)) * 100, 2) if leads else 0.0
    contact_rate = round((contactable / len(leads)) * 100, 2) if leads else 0.0
    named_rate = round((named / len(leads)) * 100, 2) if leads else 0.0
    return {
        "outputs": len(outputs),
        "leads": len(leads),
        "conversion_rate": conversion_rate,
        "consent_rate": consent_rate,
        "contact_rate": contact_rate,
        "named_rate": named_rate,
        "consented_leads": consented,
        "contactable_leads": contactable,
        "named_leads": named,
        "by_source": by_source,
        "latest_output": max((p.name for p in outputs), default=None),
    }
    consent_rate = round((consented / len(leads)) * 100, 2) if leads else 0.0
    contact_rate = round((contactable / len(leads)) * 100, 2) if leads else 0.0

    return {
        "ok": True,
        "total_leads": len(leads),
        "marketing_consented_leads": consented,
        "contactable_leads": contactable,
        "named_leads": named,
        "leads_by_source": by_source,
        "total_outputs": len(outputs),
        "lead_to_output_rate_percent": conversion_rate,
        "marketing_consent_rate_percent": consent_rate,
        "contactable_lead_rate_percent": contact_rate,
        "recent_leads": leads[-5:],
    }


# =========================
# 💰 PRODUCT GENERATION
# =========================

@app.post("/api/product-pack")
def product_pack(payload: GenerateRequest):
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
        base_url=get_base_url(),
    )
    log_lead("product-pack", payload, job_id)
    return {
        "job_id": job_id,
        "status": "queued",
        "job_url": f"{get_base_url()}/api/job/{job_id}",
        "lead_captured": bool(payload.customer_email or payload.customer_name),
    }


@app.post("/api/shorts-pack")
def shorts_pack(payload: GenerateRequest):
    job_id = create_job(
        "shorts",
        payload.model_dump(),
        build_shorts_video,
        topic=payload.topic,
        tone=payload.tone,
        promise=payload.promise,
        duration_seconds=payload.duration_seconds,
        base_url=get_base_url(),
    )
    log_lead("shorts-pack", payload, job_id)
    return {
        "job_id": job_id,
        "status": "queued",
        "job_url": f"{get_base_url()}/api/job/{job_id}",
        "lead_captured": bool(payload.customer_email or payload.customer_name),
    }


@app.post("/api/youtube-pack")
def youtube_pack(payload: GenerateRequest):
    job_id = create_job(
        "youtube",
        payload.model_dump(),
        build_youtube_pack,
        topic=payload.topic,
        niche=payload.niche,
        tone=payload.tone,
        buyer=payload.buyer,
        promise=payload.promise,
        bonus=payload.bonus,
        notes=payload.notes,
    )
    log_lead("youtube-pack", payload, job_id)
    return {
        "job_id": job_id,
        "status": "queued",
        "job_url": f"{get_base_url()}/api/job/{job_id}",
        "lead_captured": bool(payload.customer_email or payload.customer_name),
    }


@app.post("/api/product-batch")
def product_batch(payload: BatchRequest):
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
        count=payload.count,
        base_url=get_base_url(),
    )
    log_lead("product-batch", payload, job_id)
    return {
        "job_id": job_id,
        "status": "queued",
        "job_url": f"{get_base_url()}/api/job/{job_id}",
        "lead_captured": bool(payload.customer_email or payload.customer_name),
    }


@app.post("/api/shorts-batch")
def shorts_batch(payload: BatchRequest):
    job_id = create_job(
        "shorts_batch",
        payload.model_dump(),
        build_shorts_batch,
        topic=payload.topic,
        tone=payload.tone,
        promise=payload.promise,
        duration_seconds=payload.duration_seconds,
        count=payload.count,
        base_url=get_base_url(),
    )
    log_lead("shorts-batch", payload, job_id)
    return {
        "job_id": job_id,
        "status": "queued",
        "job_url": f"{get_base_url()}/api/job/{job_id}",
        "lead_captured": bool(payload.customer_email or payload.customer_name),
    }


@app.get("/api/job/{job_id}")
def job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/download/{filename}")
def download_file(filename: str):
    safe_name = Path(filename).name
    path = OUTPUT_DIR / safe_name
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=str(path), filename=quote(path.name))


@app.get("/api/outputs")
def list_outputs():
    files = []
    for path in sorted(OUTPUT_DIR.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True):
        if path.is_file():
            files.append({
                "name": path.name,
                "size": path.stat().st_size,
                "download_url": f"{get_base_url()}/api/download/{quote(path.name)}",
            })
    return {"items": files}


@app.get("/api/leads")
def list_leads():
    if not LEADS_FILE.exists():
        return {"items": [], "count": 0}
    try:
        items = json.loads(LEADS_FILE.read_text(encoding="utf-8"))
        if not isinstance(items, list):
            items = []
    except Exception:
        items = []
    return {"items": items, "count": len(items)}
ck", payload)
    result = build_youtube_pack(
        topic=payload.topic,
        niche=payload.niche,
        tone=payload.tone,
        buyer=payload.buyer,
        promise=payload.promise,
        bonus=payload.bonus,
        notes=payload.notes,
    )
    result["lead_captured"] = bool(payload.customer_email or payload.customer_name)
    return result


# =========================
# 👑 FOUNDER ROUTES
# =========================

@app.post("/api/founder/product-batch")
def founder_product_batch(payload: BatchRequest):
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
        base_url=get_base_url(),
        count=payload.count,
    )
    return {
        "job_id": job_id,
        "status": "queued",
        "job_url": f"{get_base_url()}/api/job/{job_id}",
    }


@app.post("/api/founder/shorts-batch")
def founder_shorts_batch(payload: BatchRequest):
    job_id = create_job(
        "shorts_batch",
        payload.model_dump(),
        build_shorts_batch,
        topic=payload.topic,
        tone=payload.tone,
        promise=payload.promise,
        duration_seconds=payload.duration_seconds,
        base_url=get_base_url(),
        count=payload.count,
    )
    return {
        "job_id": job_id,
        "status": "queued",
        "job_url": f"{get_base_url()}/api/job/{job_id}",
    }


# =========================
# 📊 JOB SYSTEM
# =========================

@app.get("/api/job/{job_id}")
def job_status(job_id: str):
    data = get_job(job_id)
    if data.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Job not found")
    return data


# =========================
# 📁 FILE SERVING
# =========================

@app.get("/api/file/{name}")
def serve_file(name: str):
    if "/" in name or "\\" in name:
        raise HTTPException(status_code=400, detail="Invalid file name")

    path = OUTPUT_DIR / name
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File missing")

    media_type = "application/octet-stream"
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        media_type = "application/pdf"
    elif suffix == ".mp4":
        media_type = "video/mp4"
    elif suffix == ".png":
        media_type = "image/png"
    elif suffix == ".jpg" or suffix == ".jpeg":
        media_type = "image/jpeg"
    elif suffix == ".txt":
        media_type = "text/plain; charset=utf-8"

    return FileResponse(
        path=str(path),
        media_type=media_type,
        filename=quote(path.name),
    )


@app.get("/api/outputs")
def list_outputs():
    files = []
    for path in sorted(OUTPUT_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if not path.is_file():
            continue
        files.append(
            {
                "name": path.name,
                "size": path.stat().st_size,
                "url": f"{get_base_url()}/api/file/{quote(path.name)}",
            }
        )
    return {"items": files, "count": len(files)}
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
                "download_url": f"{get_base_url()}/api/file/{quote(path.name)}",
                "url": f"/api/file/{path.name}",
                "extension": path.suffix.lower(),
            }
        )

    return {"items": items[:200]}