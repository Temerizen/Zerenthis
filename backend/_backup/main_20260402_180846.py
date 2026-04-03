from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import uuid, time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

jobs = {}

class ProductRequest(BaseModel):
    topic: str
    niche: str
    tone: str
    buyer: str
    promise: str
    bonus: str
    notes: str
    duration_seconds: int = 30

@app.get("/health")
def health():
    return {"ok": True}

def generate_product(job_id: str, payload: ProductRequest):
    time.sleep(2)

    safe_name = payload.topic.replace(" ", "_").replace("/", "_").replace("\\", "_")
    file_name = f"{safe_name}_{str(uuid.uuid4())[:6]}.txt"
    file_path = DATA_DIR / file_name

    content = f"""TITLE: {payload.topic}

NICHE: {payload.niche}
TONE: {payload.tone}
BUYER: {payload.buyer}
PROMISE: {payload.promise}
BONUS: {payload.bonus}

NOTES:
{payload.notes}
"""

    file_path.write_text(content, encoding="utf-8")

    jobs[job_id]["status"] = "completed"
    jobs[job_id]["result"] = {
        "title": payload.topic + " Execution Pack",
        "file_name": file_name,
        "file_url": f"/api/file/{file_name}"
    }

@app.post("/api/product-pack")
def create_product(payload: ProductRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "status": "queued",
        "payload": payload.model_dump(),
        "created_at": time.time()
    }

    background_tasks.add_task(generate_product, job_id, payload)
    return {"job_id": job_id, "status": "queued"}

@app.get("/api/job/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        return {"error": "not found"}
    return jobs[job_id]

@app.get("/api/file/{name}")
def get_file(name: str):
    if "/" in name or "\\" in name:
        raise HTTPException(status_code=400, detail="invalid file name")

    path = DATA_DIR / name
    if not path.exists():
        raise HTTPException(status_code=404, detail="file not found")

    return FileResponse(path, media_type="text/plain", filename=path.name)
