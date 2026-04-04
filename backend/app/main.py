from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from datetime import datetime, timezone
from pydantic import BaseModel
from uuid import uuid4
import json
import shutil

app = FastAPI(title="Zerenthis Core Engine", version="3.0")

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
OUTPUT_DIR = DATA_DIR / "outputs"
AUTO_DIR = DATA_DIR / "autopilot"
TOP_DIR = DATA_DIR / "top_performers"
CORE_DIR = DATA_DIR / "core"
MARKET_DIR = DATA_DIR / "marketplace"

JOB_FILE = DATA_DIR / "jobs.json"
WINNERS_FILE = AUTO_DIR / "winners.json"
RUNS_FILE = AUTO_DIR / "architect_runs.json"
ROADMAP_FILE = CORE_DIR / "roadmap.json"
INSIGHTS_FILE = CORE_DIR / "insights.json"
LISTINGS_FILE = MARKET_DIR / "listings.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
AUTO_DIR.mkdir(parents=True, exist_ok=True)
TOP_DIR.mkdir(parents=True, exist_ok=True)
CORE_DIR.mkdir(parents=True, exist_ok=True)
MARKET_DIR.mkdir(parents=True, exist_ok=True)

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

class WinnerIn(BaseModel):
    time: str = ""
    module: str = ""
    job_id: str = ""
    score: int = 0
    file_url: str = ""
    file_name: str = ""
    payload: dict = {}
    result: dict = {}

def now():
    return datetime.now(timezone.utc).isoformat()

def save_jobs():
    JOB_FILE.write_text(json.dumps(jobs, indent=2, ensure_ascii=False), encoding="utf-8")

def read_json_file(path, default):
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return data
    except Exception:
        pass
    return default

def write_json_file(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def read_winners():
    data = read_json_file(WINNERS_FILE, [])
    return data if isinstance(data, list) else []

def vault_top_performer(file_name: str):
    if not file_name:
        return {"vaulted": False, "reason": "missing file_name"}

    safe_name = Path(file_name).name
    source = OUTPUT_DIR / safe_name
    target = TOP_DIR / safe_name

    if not source.exists() or not source.is_file():
        return {"vaulted": False, "reason": "source file missing", "source": str(source)}

    if not target.exists():
        shutil.copy2(source, target)

    return {
        "vaulted": True,
        "source": str(source),
        "target": str(target)
    }

def append_winner(item):
    winners = read_winners()
    key = (
        str(item.get("job_id", "")),
        str(item.get("file_name", "")),
        str(item.get("module", ""))
    )

    for existing in winners:
        existing_key = (
            str(existing.get("job_id", "")),
            str(existing.get("file_name", "")),
            str(existing.get("module", ""))
        )
        if existing_key == key:
            return False, len(winners), {"vaulted": False, "reason": "duplicate"}

    vault_info = {"vaulted": False, "reason": "score below threshold"}
    try:
        score = int(item.get("score", 0) or 0)
    except Exception:
        score = 0

    if score >= 90:
        vault_info = vault_top_performer(item.get("file_name", ""))

    stored = dict(item)
    stored["vault"] = vault_info

    winners.append(stored)
    write_json_file(WINNERS_FILE, winners[-200:])
    return True, len(winners[-200:]), vault_info

def backfill_top_performers():
    winners = read_winners()
    copied = []
    missing = []

    for item in winners:
        try:
            score = int(item.get("score", 0) or 0)
        except Exception:
            score = 0

        if score < 90:
            continue

        info = vault_top_performer(item.get("file_name", ""))
        if info.get("vaulted"):
            copied.append({
                "file_name": item.get("file_name"),
                "target": info.get("target")
            })
        else:
            missing.append({
                "file_name": item.get("file_name"),
                "reason": info.get("reason"),
                "source": info.get("source", "")
            })

    return {
        "ok": True,
        "copied_count": len(copied),
        "missing_count": len(missing),
        "copied": copied,
        "missing": missing,
        "top_performers_path": str(TOP_DIR)
    }

@app.get("/")
def root():
    return {"ok": True, "message": "Zerenthis core alive"}

@app.get("/health")
def health():
    return {"ok": True, "jobs": len(jobs), "winners": len(read_winners())}

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
    winners = read_winners()
    return {
        "count": len(winners),
        "items": winners,
        "path": str(WINNERS_FILE),
        "top_performers_path": str(TOP_DIR)
    }

@app.post("/api/winners")
def add_winner(winner: WinnerIn):
    added, count, vault_info = append_winner(winner.model_dump())
    return {
        "ok": True,
        "added": added,
        "count": count,
        "path": str(WINNERS_FILE),
        "vault": vault_info
    }

@app.post("/api/top-performers/backfill")
def run_top_performer_backfill():
    return backfill_top_performers()

@app.get("/api/roadmap")
def get_roadmap():
    roadmap = read_json_file(ROADMAP_FILE, {"modules": []})
    if not isinstance(roadmap, dict):
        roadmap = {"modules": []}
    return {
        "ok": True,
        "path": str(ROADMAP_FILE),
        "roadmap": roadmap
    }

@app.get("/api/insights")
def get_insights():
    insights = read_json_file(INSIGHTS_FILE, {})
    if not isinstance(insights, dict):
        insights = {}
    return {
        "ok": True,
        "path": str(INSIGHTS_FILE),
        "insights": insights
    }

@app.get("/api/autopilot/runs")
def get_autopilot_runs():
    runs = read_json_file(RUNS_FILE, [])
    if not isinstance(runs, list):
        runs = []
    return {
        "ok": True,
        "count": len(runs),
        "path": str(RUNS_FILE),
        "items": runs[-50:]
    }

@app.get("/api/listings")
def get_listings():
    listings = read_json_file(LISTINGS_FILE, [])
    if not isinstance(listings, list):
        listings = []
    return {
        "ok": True,
        "count": len(listings),
        "path": str(LISTINGS_FILE),
        "items": listings
    }

@app.get("/api/top-performers")
def list_top_performers():
    items = []
    for p in sorted(TOP_DIR.glob("*")):
        if p.is_file():
            items.append({
                "file_name": p.name,
                "file_url": f"/api/top-performers/file/{p.name}"
            })
    return {
        "ok": True,
        "count": len(items),
        "path": str(TOP_DIR),
        "items": items
    }

@app.get("/api/top-performers/file/{name:path}")
def get_top_performer_file(name: str):
    safe_name = Path(name).name
    target = TOP_DIR / safe_name
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="top performer file not found")
    return FileResponse(str(target), filename=safe_name)

@app.get("/api/founder/overview")
def founder_overview():
    insights = read_json_file(INSIGHTS_FILE, {})
    winners = read_winners()
    roadmap = read_json_file(ROADMAP_FILE, {"modules": []})
    listings = read_json_file(LISTINGS_FILE, [])

    return {
        "ok": True,
        "system": {
            "total_jobs": len(jobs),
            "total_winners": len(winners),
            "vault_size": len(list(TOP_DIR.glob("*"))),
            "listing_count": len(listings) if isinstance(listings, list) else 0
        },
        "top_modules": insights.get("top_modules", []),
        "top_niches": insights.get("top_niches", []),
        "top_buyers": insights.get("top_buyers", []),
        "roadmap": roadmap
    }

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
