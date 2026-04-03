from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid, time, os, json

app = FastAPI()

# Allow frontend (Vercel) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

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

def generate_product(job_id, payload):
    time.sleep(2)

    file_name = payload.topic.replace(" ", "_") + "_" + str(uuid.uuid4())[:6] + ".txt"
    file_path = os.path.join(DATA_DIR, file_name)

    content = f"""
TITLE: {payload.topic}

NICHE: {payload.niche}
BUYER: {payload.buyer}
PROMISE: {payload.promise}

NOTES:
{payload.notes}
"""

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

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
        "payload": payload.dict(),
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
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        return {"error": "file not found"}
    with open(path, "r", encoding="utf-8") as f:
        return {"content": f.read()}
