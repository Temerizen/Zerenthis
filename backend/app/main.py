from fastapi import FastAPI, HTTPException, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime, timezone
import json
import os
import re
import threading
import time

from openai import OpenAI

# -----------------------------
# Storage
# -----------------------------
BASE_STORAGE = Path("/data") if Path("/data").exists() else Path(__file__).resolve().parents[2] / "backend" / "data"
DATA_DIR = BASE_STORAGE
GEN_DIR = DATA_DIR / "generated"
JOB_FILE = DATA_DIR / "jobs.json"
AUTO_FILE = DATA_DIR / "automation.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
GEN_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# App
# -----------------------------
app = FastAPI(title="Zerenthis Automation Engine", version="7.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Globals
# -----------------------------
lock = threading.Lock()
jobs: Dict[str, Dict[str, Any]] = {}
automation_state: Dict[str, Any] = {
    "enabled": False,
    "interval_minutes": 180,
    "max_daily_runs": 3,
    "runs_today": 0,
    "last_run_at": None,
    "last_reset_date": None,
    "last_job_id": None,
    "last_error": None,
    "topic_pool": [
        {
            "topic": "Make your first $100 selling AI resume kits for job seekers",
            "niche": "Make Money Online",
            "tone": "Premium",
            "buyer": "Beginners starting from zero",
            "promise": "get a first quick win",
            "bonus": "templates and prompts",
            "notes": "Keep it specific, practical, and sellable"
        },
        {
            "topic": "Sell ChatGPT prompt packs on Gumroad in 24 hours",
            "niche": "Make Money Online",
            "tone": "Premium",
            "buyer": "Beginners starting from zero",
            "promise": "launch fast",
            "bonus": "sales copy templates",
            "notes": "Focus on speed, simplicity, and first sale energy"
        },
        {
            "topic": "Faceless TikTok AI starter pack for beginners",
            "niche": "Content Monetization",
            "tone": "Premium",
            "buyer": "New creators",
            "promise": "start posting quickly",
            "bonus": "hook templates",
            "notes": "Emphasize fast setup and monetizable content angles"
        }
    ]
}
automation_thread = None
stop_event = threading.Event()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# -----------------------------
# Helpers
# -----------------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def today_utc() -> str:
    return datetime.now(timezone.utc).date().isoformat()

def slugify(value: str) -> str:
    value = (value or "product").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value[:80] or "product"

def load_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default

def save_json(path: Path, data) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)

def load_jobs() -> None:
    global jobs
    jobs = load_json(JOB_FILE, {})

def save_jobs() -> None:
    save_json(JOB_FILE, jobs)

def load_automation() -> None:
    global automation_state
    loaded = load_json(AUTO_FILE, {})
    if isinstance(loaded, dict):
        automation_state.update(loaded)

def save_automation() -> None:
    save_json(AUTO_FILE, automation_state)

def set_job(job_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    with lock:
        current = jobs.get(job_id, {})
        current.update(patch)
        jobs[job_id] = current
        save_jobs()
        return current

def set_automation(patch: Dict[str, Any]) -> Dict[str, Any]:
    with lock:
        automation_state.update(patch)
        save_automation()
        return dict(automation_state)

def build_fallback_pack(p: Dict[str, str]) -> str:
    topic = p.get("topic", "Untitled Product")
    niche = p.get("niche", "General")
    buyer = p.get("buyer", "Beginners")
    promise = p.get("promise", "get results")
    bonus = p.get("bonus", "templates and prompts")
    return f"""# {topic}

## Buyer Outcome
Help {buyer} {promise} in the {niche} niche with a practical first-win offer.

## First-Win Plan
1. Pick one micro-result.
2. Create one focused product.
3. Package it cleanly.
4. Sell it simply.
5. Improve based on feedback.

## Product Ideas
- Starter toolkit
- Prompt pack
- Checklist bundle
- Mini guide

## Bonus
{bonus}

## CTA
Launch one clean offer today and refine the winner.
"""

def generate_with_ai(p: Dict[str, str]) -> str:
    if not client:
        return build_fallback_pack(p)

    prompt = f"""
Create a premium-feeling digital product pack someone would realistically pay for.

TOPIC: {p.get("topic","")}
NICHE: {p.get("niche","")}
TONE: {p.get("tone","")}
BUYER: {p.get("buyer","")}
PROMISE: {p.get("promise","")}
BONUS: {p.get("bonus","")}
NOTES: {p.get("notes","")}

Requirements:
- Make it useful, sellable, and specific
- Include a strong title
- Include a clear buyer outcome
- Include a step-by-step first-win plan
- Include at least 7 useful prompts
- Include at least 8 product ideas tightly related to the topic
- Include a simple selling strategy
- Include a stronger CTA
- Avoid padding and vague fluff
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
    content = (response.choices[0].message.content or "").strip()
    return content or build_fallback_pack(p)

def get_best_topics(limit: int = 3) -> List[Dict[str, str]]:
    scored = [j for j in jobs.values() if isinstance(j.get("score"), int) and j.get("payload")]
    scored.sort(key=lambda x: (x.get("score", 0), x.get("created_at", "")), reverse=True)
    winners = []
    seen_topics = set()
    for j in scored:
        payload = j.get("payload", {})
        topic = payload.get("topic", "").strip()
        if topic and topic not in seen_topics:
            seen_topics.add(topic)
            winners.append(payload)
        if len(winners) >= limit:
            break
    return winners

def choose_topic_for_run() -> Dict[str, str]:
    winners = get_best_topics(limit=3)
    pool = winners if winners else automation_state.get("topic_pool", [])
    if not pool:
        return {
            "topic": "Make your first $100 selling AI starter kits online",
            "niche": "Make Money Online",
            "tone": "Premium",
            "buyer": "Beginners",
            "promise": "get a first quick win",
            "bonus": "templates and prompts",
            "notes": "Keep it practical and specific"
        }
    index = int(time.time()) % len(pool)
    return pool[index]

def run_generation(payload: Dict[str, str], automated: bool = False) -> str:
    job_id = uuid4().hex
    set_job(job_id, {
        "job_id": job_id,
        "status": "running",
        "created_at": now_iso(),
        "started_at": now_iso(),
        "payload": payload,
        "score": None,
        "notes": None,
        "error": None,
        "result": None,
        "automated": automated,
    })
    try:
        content = generate_with_ai(payload)
        filename = f"{slugify(payload.get('topic','product'))}_{job_id[:6]}.txt"
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
            "result": {"file_url": file_url}
        })
        return job_id
    except Exception as e:
        set_job(job_id, {
            "status": "failed",
            "finished_at": now_iso(),
            "error": str(e),
        })
        raise

def reset_daily_counter_if_needed() -> None:
    today = today_utc()
    if automation_state.get("last_reset_date") != today:
        set_automation({
            "runs_today": 0,
            "last_reset_date": today
        })

def automation_loop() -> None:
    while not stop_event.is_set():
        try:
            reset_daily_counter_if_needed()
            if automation_state.get("enabled"):
                runs_today = int(automation_state.get("runs_today", 0))
                max_daily_runs = int(automation_state.get("max_daily_runs", 3))
                if runs_today < max_daily_runs:
                    payload = choose_topic_for_run()
                    job_id = run_generation(payload, automated=True)
                    set_automation({
                        "runs_today": runs_today + 1,
                        "last_run_at": now_iso(),
                        "last_job_id": job_id,
                        "last_error": None
                    })
                else:
                    set_automation({"last_error": None})
            interval_minutes = max(5, int(automation_state.get("interval_minutes", 180)))
            stop_event.wait(interval_minutes * 60)
        except Exception as e:
            set_automation({
                "last_error": str(e),
                "last_run_at": now_iso()
            })
            stop_event.wait(300)

# -----------------------------
# Models
# -----------------------------
class ProductPackRequest(BaseModel):
    topic: str = ""
    niche: str = ""
    tone: str = ""
    buyer: str = ""
    promise: str = ""
    bonus: str = ""
    notes: str = ""

class AutomationConfigRequest(BaseModel):
    enabled: Optional[bool] = None
    interval_minutes: Optional[int] = None
    max_daily_runs: Optional[int] = None

# -----------------------------
# Startup
# -----------------------------
@app.on_event("startup")
def startup_event() -> None:
    global automation_thread
    load_jobs()
    load_automation()
    stop_event.clear()
    if automation_thread is None or not automation_thread.is_alive():
        automation_thread = threading.Thread(target=automation_loop, daemon=True)
        automation_thread.start()

@app.on_event("shutdown")
def shutdown_event() -> None:
    stop_event.set()

# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def root():
    return {
        "ok": True,
        "name": "Zerenthis Automation Engine",
        "version": "7.0"
    }

@app.get("/health")
def health():
    return {
        "ok": True,
        "openai_configured": bool(OPENAI_API_KEY),
        "jobs_loaded": len(jobs),
        "automation_enabled": bool(automation_state.get("enabled"))
    }

@app.post("/api/product-pack")
def create_product_pack(payload: ProductPackRequest, background_tasks: BackgroundTasks):
    job_id = uuid4().hex
    set_job(job_id, {
        "job_id": job_id,
        "status": "queued",
        "created_at": now_iso(),
        "payload": payload.dict(),
        "score": None,
        "notes": None,
        "error": None,
        "result": None,
        "automated": False,
    })

    def worker():
        try:
            set_job(job_id, {"status": "running", "started_at": now_iso()})
            content = generate_with_ai(payload.dict())
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
                "result": {"file_url": file_url}
            })
        except Exception as e:
            set_job(job_id, {
                "status": "failed",
                "finished_at": now_iso(),
                "error": str(e),
            })

    background_tasks.add_task(worker)
    return {"ok": True, "job_id": job_id, "status": "queued"}

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
    updated = set_job(job_id, {"score": score, "notes": notes})
    return {"ok": True, "job_id": job_id, "score": updated.get("score"), "notes": updated.get("notes")}

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

# -----------------------------
# Automation routes
# -----------------------------
@app.get("/api/automation/status")
def automation_status():
    reset_daily_counter_if_needed()
    return automation_state

@app.post("/api/automation/start")
def automation_start():
    reset_daily_counter_if_needed()
    updated = set_automation({"enabled": True, "last_error": None})
    return {"ok": True, "automation": updated}

@app.post("/api/automation/stop")
def automation_stop():
    updated = set_automation({"enabled": False})
    return {"ok": True, "automation": updated}

@app.post("/api/automation/config")
def automation_config(config: AutomationConfigRequest):
    patch = {}
    if config.enabled is not None:
        patch["enabled"] = bool(config.enabled)
    if config.interval_minutes is not None:
        patch["interval_minutes"] = max(5, int(config.interval_minutes))
    if config.max_daily_runs is not None:
        patch["max_daily_runs"] = max(1, int(config.max_daily_runs))
    updated = set_automation(patch)
    return {"ok": True, "automation": updated}

@app.post("/api/automation/run-once")
def automation_run_once():
    reset_daily_counter_if_needed()
    payload = choose_topic_for_run()
    job_id = run_generation(payload, automated=True)
    runs_today = int(automation_state.get("runs_today", 0))
    updated = set_automation({
        "runs_today": runs_today + 1,
        "last_run_at": now_iso(),
        "last_job_id": job_id,
        "last_error": None
    })
    return {"ok": True, "job_id": job_id, "automation": updated, "payload": payload}
