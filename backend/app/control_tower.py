from fastapi import APIRouter
from pathlib import Path
from datetime import datetime, timezone
import os, json

router = APIRouter()

DATA_DIR = Path("/data") if Path("/data").exists() else Path(__file__).resolve().parents[2] / "backend" / "data"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "backend" / "outputs"
JOB_FILE = DATA_DIR / "jobs.json"
AUTO_FILE = DATA_DIR / "automation.json"

def _read_json(path: Path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def _recent_files(limit=12):
    items = []
    if OUTPUT_DIR.exists():
        for p in OUTPUT_DIR.iterdir():
            if p.is_file():
                try:
                    stat = p.stat()
                    items.append({
                        "name": p.name,
                        "size": stat.st_size,
                        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
                    })
                except Exception:
                    pass
    items.sort(key=lambda x: x["modified_at"], reverse=True)
    return items[:limit]

@router.get("/api/control-tower")
def control_tower():
    jobs = _read_json(JOB_FILE, {})
    auto = _read_json(AUTO_FILE, {})
    recent = _recent_files()

    if isinstance(jobs, dict):
        job_list = list(jobs.values())
    elif isinstance(jobs, list):
        job_list = jobs
    else:
        job_list = []

    total_jobs = len(job_list)
    completed = sum(1 for j in job_list if str(j.get("status", "")).lower() in ("done", "completed", "success"))
    queued = sum(1 for j in job_list if str(j.get("status", "")).lower() in ("queued", "pending"))
    failed = sum(1 for j in job_list if str(j.get("status", "")).lower() in ("failed", "error"))

    latest_jobs = sorted(
        job_list,
        key=lambda j: j.get("finished_at") or j.get("started_at") or j.get("created_at") or "",
        reverse=True
    )[:10]

    return {
        "status": "ok",
        "phase": "control tower",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system": {
            "data_dir": str(DATA_DIR),
            "output_dir": str(OUTPUT_DIR),
            "jobs_file_exists": JOB_FILE.exists(),
            "automation_file_exists": AUTO_FILE.exists(),
            "output_dir_exists": OUTPUT_DIR.exists()
        },
        "jobs": {
            "total": total_jobs,
            "completed": completed,
            "queued": queued,
            "failed": failed,
            "latest": latest_jobs
        },
        "automation": auto if isinstance(auto, dict) else {"raw": auto},
        "recent_outputs": recent,
        "next_moves": [
            "generate from /api/founder/full-stack-generate",
            "check output files in /api/control-tower",
            "use strongest winners for repeat runs"
        ]
    }
