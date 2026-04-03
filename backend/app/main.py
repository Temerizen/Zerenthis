from backend.app.control_tower import router as control_tower_router
from backend.app.money_sweep import router as money_sweep_router
from backend.app.output_routes import router as output_router
from backend.app.expansion_routes import router as expansion_router
from backend.app.orchestrator_routes import router as orchestrator_router
import json
import os
from backend.app.learning_routes import router as learning_router
import json
import os
from backend.app.decision_routes import router as decision_router
from backend.app.autopilot_routes import router as autopilot_router
import json
import os
import json
import os

DATA_DIR = "backend/data"
PACKS_FILE = os.path.join(DATA_DIR, "packs.json")
os.makedirs(DATA_DIR, exist_ok=True)

def _load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _save_pack_record(topic, buyer, promise, file_name="", content=""):
    packs = _load_json(PACKS_FILE, [])
    packs.append({
        "topic": topic,
        "buyer": buyer,
        "promise": promise,
        "file_name": file_name,
        "content": content
    })
    _save_json(PACKS_FILE, packs)
from backend.app.money_routes import router as money_router
from backend.app.founder import router as founder_router
from backend.app.limit_lock import router as limit_router
from fastapi import FastAPI, BackgroundTasks, Body, HTTPException, BackgroundTasks, Body, HTTPException, BackgroundTasks, Body, HTTPException

from backend.app.evo_routes import router as evo_router
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
app = FastAPI(title="Zerenthis Evolution Engine", version="9.0")

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
    "auto_rate_enabled": True,
    "evolution_enabled": True,
    "last_seed_source": "topic_pool",
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

def heuristic_score(content: str, payload: Dict[str, str]) -> Dict[str, Any]:
    text = (content or "").lower()
    score = 4
    reasons = []

    if len(content) > 1800:
        score += 1
        reasons.append("good depth")
    if "buyer outcome" in text or "goal" in text:
        score += 1
        reasons.append("clear outcome")
    if "step-by-step" in text or "first-win" in text or "first win" in text:
        score += 1
        reasons.append("execution plan")
    if "prompt" in text:
        score += 1
        reasons.append("includes prompts")
    if "product ideas" in text or "ideas" in text:
        score += 1
        reasons.append("includes ideas")
    if "selling strategy" in text or "cta" in text or "call to action" in text:
        score += 1
        reasons.append("includes selling layer")

    topic = (payload.get("topic","") or "").lower()
    if any(word in topic for word in ["first $100", "resume", "gumroad", "tiktok", "job seekers", "24 hours"]):
        score += 1
        reasons.append("specific topic angle")

    score = max(1, min(10, score))
    notes = "auto-rated by fallback heuristic: " + ", ".join(reasons) if reasons else "auto-rated by fallback heuristic"
    return {"score": score, "notes": notes}

def auto_rate_content(content: str, payload: Dict[str, str]) -> Dict[str, Any]:
    if not client:
        return heuristic_score(content, payload)

    topic = payload.get("topic", "")
    buyer = payload.get("buyer", "")
    prompt = f"""
You are evaluating a digital product pack for sellability and usefulness.

TOPIC: {topic}
BUYER: {buyer}

Return ONLY valid JSON with this exact schema:
{{
  "score": <integer 1-10>,
  "notes": "<one concise sentence explaining the rating>"
}}

Scoring guidance:
- 9-10 = highly specific, strong buyer outcome, very sellable
- 7-8 = strong and useful, but still has some breadth or fluff
- 5-6 = decent but generic
- 1-4 = weak, repetitive, not compelling

CONTENT TO EVALUATE:
\"\"\"
{content[:12000]}
\"\"\"
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a strict product evaluator. Return only JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        raw = (response.choices[0].message.content or "").strip()
        data = json.loads(raw)
        score = int(data.get("score", 5))
        notes = str(data.get("notes", "auto-rated by AI"))
        score = max(1, min(10, score))
        return {"score": score, "notes": f"auto-rated: {notes}"}
    except Exception:
        return heuristic_score(content, payload)

def get_best_jobs(limit: int = 5) -> List[Dict[str, Any]]:
    scored = [j for j in jobs.values() if isinstance(j.get("score"), int) and j.get("payload")]
    scored.sort(key=lambda x: (x.get("score", 0), x.get("created_at", "")), reverse=True)
    return scored[:limit]

def get_best_topics(limit: int = 3) -> List[Dict[str, str]]:
    winners = []
    seen_topics = set()
    for j in get_best_jobs(limit=10):
        payload = j.get("payload", {})
        topic = payload.get("topic", "").strip()
        if topic and topic not in seen_topics:
            seen_topics.add(topic)
            winners.append(payload)
        if len(winners) >= limit:
            break
    return winners

def evolve_topic_from_winner(seed_payload: Dict[str, str]) -> Dict[str, str]:
    if not client:
        seed_topic = seed_payload.get("topic", "AI starter kit")
        return {
            "topic": f"{seed_topic} with a sharper beginner-first angle",
            "niche": seed_payload.get("niche", "Make Money Online"),
            "tone": "Premium",
            "buyer": seed_payload.get("buyer", "Beginners"),
            "promise": seed_payload.get("promise", "get results faster"),
            "bonus": seed_payload.get("bonus", "templates and prompts"),
            "notes": "Evolved from a winning topic. Make it tighter, more specific, and more sellable."
        }

    prompt = f"""
You are evolving a winning digital product topic into a stronger variant.

Seed payload:
{json.dumps(seed_payload, ensure_ascii=False)}

Return ONLY valid JSON with this exact schema:
{{
  "topic": "...",
  "niche": "...",
  "tone": "Premium",
  "buyer": "...",
  "promise": "...",
  "bonus": "...",
  "notes": "..."
}}

Rules:
- Make it more specific and more sellable than the seed
- Keep it in a niche that can monetize
- Aim for beginner-friendly clarity
- Prefer sharp first-win angles
- Avoid broad generic wording
- Do not mention being an evolved variant
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You create improved topic variants for digital products. Return only JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
        )
        raw = (response.choices[0].message.content or "").strip()
        data = json.loads(raw)
        required = ["topic", "niche", "tone", "buyer", "promise", "bonus", "notes"]
        for key in required:
            if key not in data or not str(data[key]).strip():
                raise ValueError(f"Missing evolved field: {key}")
        data["tone"] = "Premium"
        return data
    except Exception:
        seed_topic = seed_payload.get("topic", "AI starter kit")
        return {
            "topic": f"{seed_topic} for a specific beginner niche",
            "niche": seed_payload.get("niche", "Make Money Online"),
            "tone": "Premium",
            "buyer": seed_payload.get("buyer", "Beginners"),
            "promise": seed_payload.get("promise", "get a first quick win"),
            "bonus": seed_payload.get("bonus", "templates and prompts"),
            "notes": "Refine the seed topic into a tighter, more actionable offer."
        }

def choose_topic_for_run() -> Dict[str, str]:
    if automation_state.get("evolution_enabled", True):
        winners = get_best_topics(limit=3)
        if winners:
            index = int(time.time()) % len(winners)
            seed = winners[index]
            evolved = evolve_topic_from_winner(seed)
            set_automation({"last_seed_source": "winner_evolution"})
            return evolved

    pool = automation_state.get("topic_pool", [])
    if pool:
        index = int(time.time()) % len(pool)
        set_automation({"last_seed_source": "topic_pool"})
        return pool[index]

    set_automation({"last_seed_source": "fallback"})
    return {
        "topic": "Make your first $100 selling AI starter kits online",
        "niche": "Make Money Online",
        "tone": "Premium",
        "buyer": "Beginners",
        "promise": "get a first quick win",
        "bonus": "templates and prompts",
        "notes": "Keep it practical and specific"
    }

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
        "auto_rated": False,
    })
    try:
        content = generate_with_ai(payload)
        filename = f"{slugify(payload.get('topic','product'))}_{job_id[:6]}.txt"
        final_path = GEN_DIR / filename
        temp_path = GEN_DIR / f".{filename}.tmp"
        temp_path.write_text(content, encoding="utf-8")
        temp_path.replace(final_path)
        file_url = f"/api/file/{filename}"

        patch = {
            "status": "completed",
            "finished_at": now_iso(),
            "file_name": filename,
            "file_url": file_url,
            "result": {"file_url": file_url}
        }

        if automated and automation_state.get("auto_rate_enabled", True):
            rated = auto_rate_content(content, payload)
            patch["score"] = rated.get("score")
            patch["notes"] = rated.get("notes")
            patch["auto_rated"] = True

        set_job(job_id, patch)
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
    auto_rate_enabled: Optional[bool] = None
    evolution_enabled: Optional[bool] = None

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
        "name": "Zerenthis Evolution Engine",
        "version": "9.0"
    }

@app.get("/health")
def health():
    return {
        "ok": True,
        "openai_configured": bool(OPENAI_API_KEY),
        "jobs_loaded": len(jobs),
        "automation_enabled": bool(automation_state.get("enabled")),
        "auto_rate_enabled": bool(automation_state.get("auto_rate_enabled", True)),
        "evolution_enabled": bool(automation_state.get("evolution_enabled", True))
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
        "auto_rated": False,
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
    updated = set_job(job_id, {"score": score, "notes": notes, "auto_rated": False})
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
    if config.auto_rate_enabled is not None:
        patch["auto_rate_enabled"] = bool(config.auto_rate_enabled)
    if config.evolution_enabled is not None:
        patch["evolution_enabled"] = bool(config.evolution_enabled)
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

@app.get("/api/evolution/seeds")
def evolution_seeds():
    return {
        "last_seed_source": automation_state.get("last_seed_source", "unknown"),
        "top_jobs": get_best_jobs(limit=5),
        "top_topics": get_best_topics(limit=5)
    }

@app.post("/api/evolution/preview")
def evolution_preview():
    winners = get_best_topics(limit=3)
    if not winners:
        raise HTTPException(status_code=400, detail="No scored winners available yet")
    index = int(time.time()) % len(winners)
    seed = winners[index]
    evolved = evolve_topic_from_winner(seed)
    return {"ok": True, "seed": seed, "evolved": evolved}

app.include_router(evo_router)
from backend.app.video_routes import router as video_router
app.include_router(video_router)

from backend.app.surgeon_routes import router as surgeon_router
app.include_router(surgeon_router)
from backend.app.video_routes import router as video_router
app.include_router(video_router)


from backend.app.feedback_routes import router as feedback_router
app.include_router(feedback_router)
from backend.app.video_routes import router as video_router
app.include_router(video_router)

from backend.app.surgeon_routes import router as surgeon_router
app.include_router(surgeon_router)
from backend.app.video_routes import router as video_router
app.include_router(video_router)












from backend.app.file_routes import router as file_router
app.include_router(file_router)

from backend.app.winner_routes import router as winner_router
app.include_router(winner_router)

from backend.app.limit_lock import router as limit_router
app.include_router(limit_router)









@app.get("/proof")
def proof():
    return {"status": "NEW BACKEND ACTIVE"}













app.include_router(decision_router)
app.include_router(autopilot_router)


app.include_router(learning_router)


app.include_router(expansion_router)
app.include_router(orchestrator_router)




app.include_router(output_router)




from fastapi import APIRouter

from backend.app.video_factory_routes import router as video_factory_router
app.include_router(video_factory_router)


from backend.app.full_loop_routes import router as full_loop_router
app.include_router(full_loop_router)


from backend.app.body_routes import router as body_router
app.include_router(body_router)


from backend.app.distribution_routes import router as distribution_router
app.include_router(distribution_router)


from backend.app.self_improver_routes import router as self_router
app.include_router(self_router)


from backend.app.god_mode import autopilot_loop


from backend.app.reality_routes import router as reality_router
app.include_router(reality_router)


import asyncio
from backend.app.god_mode import autopilot_loop

@app.on_event("startup")
async def start_god_mode():
    asyncio.create_task(autopilot_loop())


app.include_router(money_sweep_router)


app.include_router(control_tower_router)

