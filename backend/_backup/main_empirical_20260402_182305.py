from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, Dict, Any
from uuid import uuid4
import json, re, threading

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "backend" / "data"
GEN_DIR = DATA_DIR / "generated"
JOB_FILE = DATA_DIR / "jobs.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
GEN_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Zerenthis Quality Engine", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs = {}
lock = threading.Lock()

def load():
    global jobs
    if JOB_FILE.exists():
        try: jobs = json.loads(JOB_FILE.read_text())
        except: jobs = {}

def save():
    JOB_FILE.write_text(json.dumps(jobs, indent=2))

def setj(j, d):
    with lock:
        jobs[j] = {**jobs.get(j, {}), **d}
        save()

def slug(x):
    return re.sub(r"[^a-z0-9]+","_",x.lower())[:60]

class Req(BaseModel):
    topic:str=""
    niche:str=""
    tone:str=""
    buyer:str=""
    promise:str=""
    bonus:str=""
    notes:str=""

def build(p):

    return f"""
🔥 {p.topic.upper()} — AI CASH STARTER KIT

🎯 GOAL:
Make your first $100 using AI by creating and selling a simple digital product.

--------------------------------------

⚡ EXACT METHOD (FASTEST PATH)

STEP 1 — Pick a micro-result
Example: "AI resume builder prompts"

STEP 2 — Generate product using AI
Use prompts to create:
- guide
- templates
- examples

STEP 3 — Package it
Turn it into a clean PDF or text pack

STEP 4 — Sell it
Upload to Gumroad ($9–$19)

STEP 5 — Promote
Post 3–5 short content pieces

--------------------------------------

💡 REAL PRODUCT IDEAS

1. "AI Resume Toolkit"
2. "ChatGPT Side Hustle Prompts"
3. "Faceless TikTok AI Guide"
4. "AI Business Name Generator Kit"

--------------------------------------

📦 YOUR FIRST PRODUCT (EXAMPLE)

Title:
"{p.topic} Starter Kit"

Price:
$9

Inside:
- guide
- prompts
- templates

--------------------------------------

🧩 HIGH VALUE PROMPTS

1. "Create a beginner-friendly product about {p.topic}"
2. "Write a sales page for a {p.niche} product"
3. "Generate 10 TikTok hooks about {p.topic}"
4. "Create a step-by-step guide for {p.buyer}"
5. "Write a simple Gumroad description"
6. "Generate 5 product ideas in {p.niche}"

--------------------------------------

🚀 HOW TO GET YOUR FIRST SALE

1. Generate product (10–15 min)
2. Upload to Gumroad
3. Post:
   - 3 TikToks OR
   - 1 Twitter thread
4. Use hook:
   "I made this with AI in 20 minutes"

--------------------------------------

🎯 HOOKS THAT SELL

- "This AI trick made me my first sale"
- "I used ChatGPT to create income"
- "You’re one prompt away from your first product"

--------------------------------------

⚠️ FINAL TRUTH

This works because:
- low cost
- fast creation
- high demand

The only rule:
EXECUTE FAST.

"""

def process(j,p):
    try:
        setj(j,{"status":"running"})
        name = slug(p.topic)+"_"+j[:6]+".txt"
        path = GEN_DIR / name

        path.write_text(build(p))

        url = f"/api/file/{name}"

        setj(j,{
            "status":"completed",
            "file_url":url,
            "result":{"file_url":url}
        })

    except Exception as e:
        setj(j,{"status":"failed","error":str(e)})

@app.on_event("startup")
def s(): load()

@app.get("/health")
def h(): return {"ok":True}

@app.post("/api/product-pack")
def create(p:Req, bg:BackgroundTasks):
    jid = uuid4().hex
    setj(jid,{"status":"queued"})
    bg.add_task(process,jid,p)
    return {"job_id":jid}

@app.get("/api/job/{jid}")
def get(jid:str):
    if jid not in jobs: raise HTTPException(404)
    return jobs[jid]

@app.get("/api/file/{name}")
def f(name:str):
    p = GEN_DIR / name
    if not p.exists(): raise HTTPException(404)
    return FileResponse(p)
