from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from Engine.jobs import create_job, get_job
from Engine.product_engine import build_product_batch, build_product_pack
from Engine.video_engine import build_shorts_batch, build_shorts_video, build_youtube_pack

APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
OUTPUT_DIR = BACKEND_DIR / "data" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Zerenthis Automation Core")

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


def get_base_url() -> str:
    return ""


@app.get("/")
def root():
    return {"status": "Zerenthis Automation Core Live"}


@app.get("/health")
def health():
    return {"ok": True}


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
    return {"job_id": job_id, "status": "queued"}


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
    return {"job_id": job_id, "status": "queued"}


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
