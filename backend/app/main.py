from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from datetime import datetime, timezone
from pydantic import BaseModel
from uuid import uuid4
import json

app = FastAPI(title="Zerenthis Recovery Core", version="1.0")

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
OUTPUT_DIR = DATA_DIR / "outputs"
JOB_FILE = DATA_DIR / "jobs.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

@app.get("/")
def root():
    return {"ok": True, "message": "recovery core alive"}

@app.get("/health")
def health():
    return {"ok": True, "message": "health alive", "jobs": len(jobs)}

@app.post("/api/product-pack")
def create_product_pack(payload: ProductPackRequest):
    job_id = uuid4().hex
    file_name = f"{job_id}.txt"
    file_path = OUTPUT_DIR / file_name

    content = f"""TOPIC: {payload.topic}
NICHE: {payload.niche}
TONE: {payload.tone}
BUYER: {payload.buyer}
PROMISE: {payload.promise}
BONUS: {payload.bonus}
NOTES: {payload.notes}
"""

    file_path.write_text(content, encoding="utf-8")

    jobs[job_id] = {
        "job_id": job_id,
        "status": "completed",
        "created_at": now(),
        "payload": payload.model_dump(),
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

@app.get("/api/job/{job_id}")
def get_job(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/api/jobs")
def list_jobs():
    return list(jobs.values())

@app.get("/api/file/{name:path}")
def get_file(name: str):
    safe_name = Path(name).name
    target = OUTPUT_DIR / safe_name
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(str(target), filename=safe_name)
