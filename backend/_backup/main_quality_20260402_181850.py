from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, Dict, Any
from uuid import uuid4
from datetime import datetime, timezone
import json, re, threading

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "backend" / "data"
GEN_DIR = DATA_DIR / "generated"
JOB_FILE = DATA_DIR / "jobs.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
GEN_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Zerenthis Money Engine", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

job_lock = threading.Lock()
jobs: Dict[str, Dict[str, Any]] = {}

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def safe_slug(v):
    v = (v or "product").lower()
    v = re.sub(r"[^a-z0-9]+","_",v)
    return v[:60]

def load_jobs():
    global jobs
    if JOB_FILE.exists():
        try: jobs = json.loads(JOB_FILE.read_text())
        except: jobs = {}
    else: jobs = {}

def save_jobs():
    JOB_FILE.write_text(json.dumps(jobs, indent=2))

def set_job(jid, data):
    with job_lock:
        jobs[jid] = {**jobs.get(jid, {}), **data}
        save_jobs()

class ProductPackRequest(BaseModel):
    topic:str=""
    niche:str=""
    tone:str=""
    buyer:str=""
    promise:str=""
    bonus:str=""
    notes:str=""

def build_money_pack(p):

    return f"""
🔥 {p.topic.upper()} — PREMIUM AI PRODUCT PACK

WHO THIS IS FOR:
{p.buyer}

CORE RESULT:
This product helps the user {p.promise} using AI with a clear step-by-step system.

--------------------------------------

💰 SECTION 1: THE OPPORTUNITY

Right now, people are making money using AI by:
- creating digital products
- selling simple guides
- building niche content systems

The advantage? Speed and leverage.

--------------------------------------

⚡ SECTION 2: THE SIMPLE MONEY SYSTEM

STEP 1 — Pick a specific outcome
STEP 2 — Generate a product around it
STEP 3 — Package it cleanly
STEP 4 — Sell it on Gumroad or similar
STEP 5 — Improve what works

--------------------------------------

🧠 SECTION 3: PRODUCT IDEAS

- AI beginner income kit
- niche-specific AI workflows
- shortcut guides
- automation packs

--------------------------------------

📦 SECTION 4: YOUR SELLABLE PRODUCT

Title Idea:
"{p.topic} — Starter Kit"

Price:
$9–$19

What to include:
- Guide (this document)
- Templates
- Prompts

--------------------------------------

🧩 SECTION 5: TEMPLATES (HIGH VALUE)

PROMPT TEMPLATE:
"Generate a {p.niche} product that helps {p.buyer} achieve {p.promise}"

OFFER TEMPLATE:
"This guide helps you {p.promise} using AI without wasting time."

--------------------------------------

🚀 SECTION 6: HOW TO SELL IT

1. Upload to Gumroad
2. Add simple title + description
3. Post content on TikTok / Twitter
4. Drive traffic to product

--------------------------------------

🎯 SECTION 7: HOOKS

- "AI is replacing beginners — unless you do this"
- "Turn AI into income in 24 hours"
- "Start making money with AI even if you're starting from zero"

--------------------------------------

⚠️ FINAL NOTE

This is not theory.

This is a simple system:
Create → Package → Sell → Improve

Speed wins.

"""

def process(jid,p):
    try:
        set_job(jid, {"status":"running"})
        slug = safe_slug(p.topic)
        name = f"{slug}_{jid[:6]}.txt"
        path = GEN_DIR / name

        content = build_money_pack(p)
        path.write_text(content)

        url = f"/api/file/{name}"

        set_job(jid,{
            "status":"completed",
            "file_url":url,
            "file_name":name,
            "result":{"file_url":url}
        })

    except Exception as e:
        set_job(jid,{"status":"failed","error":str(e)})

@app.on_event("startup")
def s(): load_jobs()

@app.get("/health")
def h(): return {"ok":True}

@app.post("/api/product-pack")
def create(p:ProductPackRequest, bg:BackgroundTasks):
    jid = uuid4().hex
    set_job(jid,{"status":"queued"})
    bg.add_task(process,jid,p)
    return {"job_id":jid}

@app.get("/api/job/{jid}")
def get(jid:str):
    j = jobs.get(jid)
    if not j: raise HTTPException(404,"Not found")
    return j

@app.get("/api/file/{name}")
def f(name:str):
    p = GEN_DIR / name
    if not p.exists(): raise HTTPException(404)
    return FileResponse(p)
