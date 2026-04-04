from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from datetime import datetime, timezone
from pydantic import BaseModel
from uuid import uuid4
import json

app = FastAPI(title="Zerenthis Core Engine", version="2.1")

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
OUTPUT_DIR = DATA_DIR / "outputs"
AUTO_DIR = DATA_DIR / "autopilot"
JOB_FILE = DATA_DIR / "jobs.json"
WINNERS_FILE = AUTO_DIR / "winners.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
AUTO_DIR.mkdir(parents=True, exist_ok=True)

jobs = {}

if JOB_FILE.exists():
    try:
        jobs = json.loads(JOB_FILE.read_text(encoding="utf-8"))
        if not isinstance(jobs, dict):
            jobs = {}
    except Exception:
        jobs = {}

class ProductPackRequest(BaseModel):
    topic: str = ""
    niche: str = ""
    tone: str = ""
    buyer: str = ""
    promise: str = ""
    bonus: str = ""
    notes: str = ""

def now():
    return datetime.now(timezone.utc).isoformat()

def save_jobs():
    JOB_FILE.write_text(json.dumps(jobs, indent=2, ensure_ascii=False), encoding="utf-8")

def read_winners():
    if WINNERS_FILE.exists():
        try:
            data = json.loads(WINNERS_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return []

@app.get("/")
def root():
    return {"ok": True, "message": "Zerenthis core alive"}

@app.get("/health")
def health():
    return {"ok": True, "jobs": len(jobs)}

@app.get("/api/jobs")
def list_jobs():
    return list(jobs.values())

@app.get("/api/job/{job_id}")
def get_job(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/api/winners")
def get_winners():
    return read_winners()

@app.post("/api/product-pack")
def create_product_pack(payload: ProductPackRequest):
    job_id = uuid4().hex

    try:
        from backend.Engine.product_engine import build_product_pack
        result = build_product_pack(**payload.model_dump())

        file_name = Path(result.get("file_name", f"{job_id}.txt")).name
        file_path = OUTPUT_DIR / file_name

        if not file_path.exists():
            content = json.dumps(result, indent=2, ensure_ascii=False)
            file_path.write_text(content, encoding="utf-8")

    except Exception as e:
        file_name = f"{job_id}.txt"
        file_path = OUTPUT_DIR / file_name
        content = f"""FALLBACK MODE

ERROR: {str(e)}

TOPIC: {payload.topic}
NICHE: {payload.niche}
TONE: {payload.tone}
BUYER: {payload.buyer}
PROMISE: {payload.promise}
BONUS: {payload.bonus}
NOTES: {payload.notes}
"""
        file_path.write_text(content, encoding="utf-8")
        result = {"error": str(e), "fallback": True}

    jobs[job_id] = {
        "job_id": job_id,
        "status": "completed",
        "created_at": now(),
        "payload": payload.model_dump(),
        "result": result,
        "file_name": file_name,
        "file_url": f"/api/file/{file_name}"
    }

    save_jobs()

    return {
        "ok": True,
        "job_id": job_id,
        "status": "completed",
        "file_url": f"/api/file/{file_name}"
    }

@app.get("/api/file/{name:path}")
def get_file(name: str):
    safe_name = Path(name).name
    target = OUTPUT_DIR / safe_name
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(str(target), filename=safe_name)
