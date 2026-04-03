from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, Dict, Any
from uuid import uuid4
from datetime import datetime
import json, os, threading, re

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "backend" / "data"
GEN_DIR = DATA_DIR / "generated"
JOB_FILE = DATA_DIR / "jobs.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
GEN_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Zerenthis AI Engine", version="5.0")

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

def setj(j,d):
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

def generate_with_ai(p):

    prompt = f"""
Create a HIGH QUALITY digital product pack that someone would PAY for.

Topic: {p.topic}
Audience: {p.buyer}
Niche: {p.niche}

Requirements:
- clear way to make first $100
- include step-by-step plan
- include 5+ real prompts
- include product ideas
- include selling strategy
- make it feel premium and actionable
- no fluff
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )

    return res.choices[0].message.content

def process(j,p):
    try:
        setj(j,{"status":"running"})

        content = generate_with_ai(p)

        name = slug(p.topic)+"_"+j[:6]+".txt"
        path = GEN_DIR / name
        path.write_text(content)

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
