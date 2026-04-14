import os
import json
import time
import traceback
import subprocess
from pathlib import Path
from datetime import datetime
import requests

from backend.proposal_engine import build_proposal, set_module_status, mark_proposal_status

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE / "backend" / "data"
AUTO = DATA_DIR / "autopilot"
RUNS = AUTO / "architect_runs.json"

BASE_URL = os.getenv("BASE_URL") or os.getenv("PUBLIC_BASE_URL") or "http://semantiqai-backend.railway.internal:8080"
TIMEOUT = 180

MODULE_MAP = {
    "Money Engine": {
        "topic": "AI money engine starter system for beginners",
        "niche": "Content Monetization",
        "buyer": "Beginners",
        "tone": "Premium",
        "promise": "start making money faster",
        "bonus": "templates and hooks",
        "notes": "roadmap execution: Money Engine"
    },
    "Content Factory": {
        "topic": "Automated content factory for creators",
        "niche": "Content Monetization",
        "buyer": "Creators",
        "tone": "Premium",
        "promise": "produce more content faster",
        "bonus": "distribution templates",
        "notes": "roadmap execution: Content Factory"
    },
    "Video Engine": {
        "topic": "Automated video engine for faceless content",
        "niche": "Content Monetization",
        "buyer": "Creators",
        "tone": "Premium",
        "promise": "publish videos faster",
        "bonus": "video hooks",
        "notes": "roadmap execution: Video Engine"
    },
    "Founder Console": {
        "topic": "Founder control dashboard for AI operations",
        "niche": "Automation",
        "buyer": "Founders",
        "tone": "Premium",
        "promise": "control systems clearly",
        "bonus": "review panel ideas",
        "notes": "roadmap execution: Founder Console"
    }
}

def now():
    return datetime.utcnow().isoformat()

def read_json(path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def append_run(entry):
    data = read_json(RUNS, [])
    if not isinstance(data, list):
        data = []
    data.append(entry)
    write_json(RUNS, data[-300:])

def verify_health():
    r = requests.get(f"{BASE_URL}/health", timeout=60)
    r.raise_for_status()
    data = r.json()
    return data.get("ok") is True

def push_winner(entry):
    r = requests.post(f"{BASE_URL}/api/winners", json=entry, timeout=60)
    r.raise_for_status()
    print("=== WINNER PUSHED TO MAIN ===")
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))

def run_ascension():
    try:
        result = subprocess.run(
            ["python", "-m", "backend.ascension_engine"],
            capture_output=True,
            text=True,
            timeout=120
        )
        print("=== ASCENSION ENGINE ===")
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except Exception as e:
        print("=== ASCENSION ENGINE ERROR ===")
        print(str(e))

def execute_proposal(proposal):
    module = proposal["module"]
    risk = proposal.get("risk", "medium")

    if risk != "low":
        set_module_status(module, "blocked", {"blocked_reason": f"risk={risk} requires approval"})
        mark_proposal_status(proposal["id"], "blocked", {"blocked_reason": f"risk={risk} requires approval"})
        return {"status": "blocked", "reason": f"risk={risk} requires approval"}

    payload = MODULE_MAP.get(module)
    if not payload:
        set_module_status(module, "blocked", {"blocked_reason": "no execution mapping"})
        mark_proposal_status(proposal["id"], "blocked", {"blocked_reason": "no execution mapping"})
        return {"status": "blocked", "reason": "no execution mapping"}

    set_module_status(module, "building", {"started_at": now()})
    mark_proposal_status(proposal["id"], "building", {"started_at": now()})

    response = requests.post(f"{BASE_URL}/api/product-pack", json=payload, timeout=TIMEOUT)
    response.raise_for_status()
    result = response.json()

    job_id = result.get("job_id")
    job = {}
    if job_id:
        time.sleep(4)
        jr = requests.get(f"{BASE_URL}/api/job/{job_id}", timeout=60)
        jr.raise_for_status()
        job = jr.json()

    health_ok = verify_health()
    success = bool(result) and health_ok

    if success:
        set_module_status(module, "complete", {
            "completed_at": now(),
            "last_result": "ok",
            "last_job_id": job_id
        })
        mark_proposal_status(proposal["id"], "complete", {
            "completed_at": now(),
            "result_summary": "executed and verified",
            "job_id": job_id
        })

        summary = (job.get("result") or {}).get("summary") or {}
        score = summary.get("quality_score", 0)

        push_winner({
            "time": now(),
            "module": module,
            "job_id": job_id,
            "score": score,
            "file_url": job.get("file_url"),
            "file_name": job.get("file_name"),
            "payload": job.get("payload") or {},
            "result": job.get("result") or {}
        })

        run_ascension()

        return {
            "status": "complete",
            "result": result,
            "job": job,
            "verified": True
        }

    set_module_status(module, "blocked", {"blocked_reason": "verification failed"})
    mark_proposal_status(proposal["id"], "blocked", {"blocked_reason": "verification failed"})
    return {"status": "blocked", "reason": "verification failed", "result": result, "job": job}

def loop():
    while True:
        try:
            proposal = build_proposal()
            print("=== ARCHITECT PROPOSAL ===")
            print(json.dumps(proposal, indent=2, ensure_ascii=False))

            if proposal.get("status") == "complete":
                append_run({"time": now(), "status": "complete", "proposal": proposal})
                run_ascension()
                time.sleep(300)
                continue

            outcome = execute_proposal(proposal)

            print("=== EXECUTION OUTCOME ===")
            print(json.dumps(outcome, indent=2, ensure_ascii=False))

            append_run({
                "time": now(),
                "proposal": proposal,
                "outcome": outcome
            })

        except Exception as e:
            err = {
                "time": now(),
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print("=== ARCHITECT ERROR ===")
            print(json.dumps(err, indent=2, ensure_ascii=False))
            append_run(err)

        time.sleep(300)

if __name__ == "__main__":
    loop()





