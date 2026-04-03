from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, Dict, Any
from uuid import uuid4
from datetime import datetime, timezone
import json
import re
import threading

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "backend" / "data"
GEN_DIR = DATA_DIR / "generated"
JOB_FILE = DATA_DIR / "jobs.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
GEN_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Zerenthis Stable Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

job_lock = threading.Lock()
jobs: Dict[str, Dict[str, Any]] = {}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_slug(value: str) -> str:
    value = (value or "generated_product").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value[:80] or "generated_product"


def load_jobs() -> None:
    global jobs
    if JOB_FILE.exists():
        try:
            jobs = json.loads(JOB_FILE.read_text(encoding="utf-8"))
        except Exception:
            jobs = {}
    else:
        jobs = {}


def save_jobs() -> None:
    tmp = JOB_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(jobs, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(JOB_FILE)


def set_job(job_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    with job_lock:
        current = jobs.get(job_id, {})
        current.update(patch)
        jobs[job_id] = current
        save_jobs()
        return current


def build_product_text(payload: "ProductPackRequest") -> str:
    title = payload.topic.strip() or "Untitled Product"
    niche = payload.niche.strip() or "General"
    tone = payload.tone.strip() or "Clear"
    buyer = payload.buyer.strip() or "General audience"
    promise = payload.promise.strip() or "get a useful result"
    bonus = payload.bonus.strip() or "extra templates"
    notes = payload.notes.strip() or "Keep it practical"
    created = datetime.now().strftime("%B %d, %Y")

    return f"""# {title}

Created: {created}
Niche: {niche}
Tone: {tone}
Ideal Buyer: {buyer}
Core Promise: {promise}
Bonus: {bonus}

## Quick Positioning
This guide is designed for {buyer.lower()} in the {niche.lower()} space. The goal is to help the reader {promise} using a practical, premium-feeling approach that avoids fluff and focuses on momentum.

## The Fastest Path
1. Pick one outcome people already want.
2. Use AI to create a focused offer around that outcome.
3. Package the result into a simple asset like a guide, checklist, template pack, or prompt pack.
4. Publish it where buying friction is low.
5. Improve the winner instead of jumping to ten different ideas.

## Offer Angle
A strong beginner-friendly angle for this topic is:
"Start simple, move fast, and use AI to compress the learning curve."

## Starter Framework
- Problem: The buyer wants a faster path without wasting time.
- Solution: A repeatable AI-assisted workflow.
- Result: Quicker execution, less confusion, and a clearer first win.

## Sellable Pack Structure
### 1) Core Guide
Explain the topic in plain language and make the first win feel reachable.

### 2) Action Steps
Give the buyer a small sequence they can complete today:
- define the niche
- choose one product angle
- generate the first asset
- polish the headline
- publish the offer

### 3) Templates
Include reusable fill-in-the-blank templates and prompts so the buyer is not starting from zero.

### 4) Bonus
Add {bonus} to increase perceived value.

## Example Hooks
- How beginners can use AI to get moving faster in 2026
- A simpler way to turn AI into a practical income tool
- Start with one offer, one audience, and one clean workflow

## Quick CTA Ideas
- Download the starter guide
- Get the templates and prompts
- Use this pack to launch your first simple offer

## Notes For Improvement
{notes}

## Final Thought
This asset is meant to be a working first version, not the final empire. The fastest growth comes from publishing, learning, and refining the winner.

"""

class ProductPackRequest(BaseModel):
    topic: str = ""
    niche: str = ""
    tone: str = ""
    buyer: str = ""
    promise: str = ""
    bonus: str = ""
    notes: str = ""
    duration_seconds: Optional[int] = 35


def process_job(job_id: str, payload: ProductPackRequest) -> None:
    try:
        set_job(job_id, {
            "status": "running",
            "started_at": now_iso(),
            "error": None,
        })

        title = payload.topic.strip() or "Generated Product Pack"
        slug = safe_slug(title)
        short_id = job_id[:8]
        filename = f"{slug}_{short_id}.txt"
        final_path = GEN_DIR / filename
        temp_path = GEN_DIR / f".{filename}.tmp"

        content = build_product_text(payload)
        temp_path.write_text(content, encoding="utf-8")
        temp_path.replace(final_path)

        file_url = f"/api/file/{filename}"

        set_job(job_id, {
            "status": "completed",
            "finished_at": now_iso(),
            "title": title,
            "file_name": filename,
            "file_path": str(final_path),
            "file_url": file_url,
            "result": {
                "title": title,
                "summary": "Product pack generated successfully.",
                "file_name": filename,
                "file_url": file_url,
            },
        })
    except Exception as e:
        set_job(job_id, {
            "status": "failed",
            "finished_at": now_iso(),
            "error": str(e),
        })


@app.on_event("startup")
def startup_event() -> None:
    load_jobs()


@app.get("/")
def root():
    return {
        "ok": True,
        "name": "Zerenthis Stable Backend",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "zerenthis-backend",
        "jobs_loaded": len(jobs),
        "generated_dir": str(GEN_DIR)
    }


@app.post("/api/product-pack")
def create_product_pack(payload: ProductPackRequest, background_tasks: BackgroundTasks):
    job_id = uuid4().hex
    created_at = now_iso()

    set_job(job_id, {
        "job_id": job_id,
        "kind": "product_pack",
        "status": "queued",
        "created_at": created_at,
        "payload": payload.dict(),
        "error": None,
        "result": None,
    })

    background_tasks.add_task(process_job, job_id, payload)

    return {
        "ok": True,
        "job_id": job_id,
        "status": "queued",
        "message": "Product pack job created."
    }


@app.get("/api/job/{job_id}")
def get_job(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response = {
        "job_id": job.get("job_id", job_id),
        "kind": job.get("kind"),
        "status": job.get("status", "unknown"),
        "created_at": job.get("created_at"),
        "started_at": job.get("started_at"),
        "finished_at": job.get("finished_at"),
        "title": job.get("title"),
        "error": job.get("error"),
        "result": job.get("result"),
        "file_name": job.get("file_name"),
        "file_url": job.get("file_url"),
    }

    if response["status"] == "completed" and not response["file_url"]:
        response["status"] = "failed"
        response["error"] = "Job marked completed without a file_url."
        set_job(job_id, {
            "status": "failed",
            "error": response["error"],
            "finished_at": now_iso(),
        })

    return response


@app.get("/api/file/{filename}")
def get_file(filename: str):
    safe_name = Path(filename).name
    path = GEN_DIR / safe_name
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=safe_name, media_type="text/plain")
