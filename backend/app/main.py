from fastapi import FastAPI, HTTPException, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime, timezone
import json, re, threading

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "backend" / "data"
GEN_DIR = DATA_DIR / "generated"
JOB_FILE = DATA_DIR / "jobs.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
GEN_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Zerenthis Empirical Engine", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

lock = threading.Lock()
jobs: Dict[str, Dict[str, Any]] = {}

def now():
    return datetime.now(timezone.utc).isoformat()

def slug(x):
    return re.sub(r"[^a-z0-9]+","_", (x or "product").lower())[:60]

def load():
    global jobs
    if JOB_FILE.exists():
        try: jobs = json.loads(JOB_FILE.read_text())
        except: jobs = {}
    else:
        jobs = {}

def save():
    tmp = JOB_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(jobs, indent=2))
    tmp.replace(JOB_FILE)

def setj(jid, data):
    with lock:
        jobs[jid] = {**jobs.get(jid, {}), **data}
        save()
        return jobs[jid]

class Req(BaseModel):
    topic:str=""
    niche:str=""
    tone:str=""
    buyer:str=""
    promise:str=""
    bonus:str=""
    notes:str=""

def build(p: Req):
    return f"""
🔥 {p.topic.upper()} — AI CASH STARTER KIT

🎯 GOAL:
Make your first $100 using AI by creating and selling a simple digital product.

--------------------------------------

⚡ EXACT METHOD

1. Pick a micro-result
2. Generate product with AI
3. Package it
4. Sell it ($9–$19)
5. Promote with short content

--------------------------------------

💡 PRODUCT IDEAS
- AI resume toolkit
- ChatGPT prompt packs
- faceless TikTok guides

--------------------------------------

🧩 PROMPTS
- Create product about {p.topic}
- Write sales page for {p.niche}
- Generate TikTok hooks

--------------------------------------

🚀 FIRST SALE PLAN
- Generate in 15 min
- Upload to Gumroad
- Post 3 pieces of content

--------------------------------------

EXECUTE FAST.
"""

def process(jid, p):
    try:
        setj(jid, {
            "status":"running",
            "started_at": now()
        })

        name = slug(p.topic) + "_" + jid[:6] + ".txt"
        path = GEN_DIR / name

        content = build(p)
        path.write_text(content)

        url = f"/api/file/{name}"

        setj(jid, {
            "status":"completed",
            "finished_at": now(),
            "file_url": url,
            "file_name": name,
            "payload": p.dict(),
            "score": None,
            "notes": None,
            "result": {"file_url": url}
        })

    except Exception as e:
        setj(jid, {
            "status":"failed",
            "error": str(e),
            "finished_at": now()
        })

@app.on_event("startup")
def startup():
    load()

@app.get("/health")
def health():
    return {"ok": True, "jobs": len(jobs)}

@app.post("/api/product-pack")
def create(p: Req, bg: BackgroundTasks):
    jid = uuid4().hex
    setj(jid, {
        "job_id": jid,
        "status":"queued",
        "created_at": now(),
        "payload": p.dict()
    })
    bg.add_task(process, jid, p)
    return {"job_id": jid}

@app.get("/api/job/{jid}")
def get(jid: str):
    j = jobs.get(jid)
    if not j:
        raise HTTPException(404)
    return j

@app.get("/api/jobs")
def list_jobs():
    return list(jobs.values())

@app.post("/api/job/{jid}/rate")
def rate_job(jid: str, score: int = Body(...), notes: Optional[str] = Body(None)):
    if jid not in jobs:
        raise HTTPException(404)
    if score < 1 or score > 10:
        raise HTTPException(400, "Score must be 1-10")

    setj(jid, {
        "score": score,
        "notes": notes
    })

    return {"ok": True}

@app.get("/api/top")
def top_jobs(limit: int = 5):
    scored = [j for j in jobs.values() if j.get("score") is not None]
    scored.sort(key=lambda x: x.get("score", 0), reverse=True)
    return scored[:limit]

@app.get("/api/file/{name}")
def file(name: str):
    p = GEN_DIR / name
    if not p.exists():
        raise HTTPException(404)
    return FileResponse(p)
