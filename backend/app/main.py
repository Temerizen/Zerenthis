from fastapi import FastAPI, HTTPException, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, Dict, Any
from uuid import uuid4
from datetime import datetime, timezone
import json
import os
import re
import threading

from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "backend" / "data"
GEN_DIR = DATA_DIR / "generated"
JOB_FILE = DATA_DIR / "jobs.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
GEN_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Zerenthis AI Empirical Engine", version="6.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

lock = threading.Lock()
jobs: Dict[str, Dict[str, Any]] = {}

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    value = (value or "product").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value[:80] or "product"


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
    with lock:
        current = jobs.get(job_id, {})
        current.update(patch)
        jobs[job_id] = current
        save_jobs()
        return current


class ProductPackRequest(BaseModel):
    topic: str = ""
    niche: str = ""
    tone: str = ""
    buyer: str = ""
    promise: str = ""
    bonus: str = ""
    notes: str = ""


def build_fallback_pack(p: ProductPackRequest) -> str:
    topic = p.topic or "Untitled Product"
    niche = p.niche or "General"
    buyer = p.buyer or "Beginners"
    promise = p.promise or "get results"
    bonus = p.bonus or "templates and prompts"

    return f"""# {topic} — AI Cash Starter Kit

## Goal
Help {buyer} {promise} using a practical digital product in the {niche} niche.

## Fast Path
1. Pick one micro-result.
2. Generate a focused product around that result.
3. Package it cleanly.
4. Sell it simply.
5. Improve the winner.

## Product Ideas
- Starter toolkit
- Prompt pack
- Checklist bundle
- Mini guide

## Included Bonus
{bonus}

## First Sale Plan
- Create one clean offer
- Publish it fast
- Post 3 short content pieces
- Iterate based on response
"""


def generate_with_ai(p: ProductPackRequest) -> str:
    if not client:
        return build_fallback_pack(p)

    prompt = f"""
Create a premium-feeling digital product pack someone would realistically pay for.

TOPIC: {p.topic}
NICHE: {p.niche}
TONE: {p.tone}
BUYER: {p.buyer}
PROMISE: {p.promise}
BONUS: {p.bonus}
NOTES: {p.notes}

Requirements:
- Make it feel useful and sellable, not fluffy
- Include a strong title
- Include a clear buyer outcome
- Include a step-by-step first-win plan
- Include at least 7 useful prompts
- Include at least 8 product ideas tightly related to the topic
- Include a simple selling strategy
- Include a stronger CTA
- Be specific and practical
- Avoid pretending something is 30 pages long unless the content actually supports that
- Output in clean plain text with strong section headers
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You create concise but premium digital product packs for online selling."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.9,
    )
    return (response.choices[0].message.content or "").strip() or build_fallback_pack(p)


def process_job(job_id: str, payload: ProductPackRequest) -> None:
    try:
        set_job(job_id, {
            "status": "running",
            "started_at": now_iso(),
            "error": None,
        })

        content = generate_with_ai(payload)

        filename = f"{slugify(payload.topic)}_{job_id[:6]}.txt"
        final_path = GEN_DIR / filename
        temp_path = GEN_DIR / f".{filename}.tmp"

        temp_path.write_text(content, encoding="utf-8")
        temp_path.replace(final_path)

        file_url = f"/api/file/{filename}"

        set_job(job_id, {
            "status": "completed",
            "finished_at": now_iso(),
            "file_name": filename,
            "file_url": file_url,
            "result": {
                "file_url": file_url
            }
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
        "name": "Zerenthis AI Empirical Engine",
        "version": "6.0"
    }


@app.get("/health")
def health():
    return {
        "ok": True,
        "openai_configured": bool(OPENAI_API_KEY),
        "jobs_loaded": len(jobs)
    }


@app.post("/api/product-pack")
def create_product_pack(payload: ProductPackRequest, background_tasks: BackgroundTasks):
    job_id = uuid4().hex
    set_job(job_id, {
        "job_id": job_id,
        "status": "queued",
        "created_at": now_iso(),
        "payload": payload.dict(),
        "score": jobs.get(job_id, {}).get("score"),
        "notes": jobs.get(job_id, {}).get("notes"),
        "error": None,
        "result": None,
    })
    background_tasks.add_task(process_job, job_id, payload)
    return {
        "ok": True,
        "job_id": job_id,
        "status": "queued"
    }


@app.get("/api/job/{job_id}")
def get_job(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/jobs")
def list_jobs():
    items = list(jobs.values())
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return items


@app.post("/api/job/{job_id}/rate")
def rate_job(
    job_id: str,
    score: int = Body(..., embed=True),
    notes: Optional[str] = Body(None, embed=True)
):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if score < 1 or score > 10:
        raise HTTPException(status_code=400, detail="Score must be 1-10")

    updated = set_job(job_id, {
        "score": score,
        "notes": notes
    })
    return {
        "ok": True,
        "job_id": job_id,
        "score": updated.get("score"),
        "notes": updated.get("notes")
    }


@app.get("/api/top")
def top_jobs(limit: int = 5):
    scored = [j for j in jobs.values() if isinstance(j.get("score"), int)]
    scored.sort(key=lambda x: (x.get("score", 0), x.get("created_at", "")), reverse=True)
    return scored[:limit]


@app.get("/api/file/{filename}")
def get_file(filename: str):
    safe_name = Path(filename).name
    path = GEN_DIR / safe_name
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=safe_name, media_type="text/plain")
