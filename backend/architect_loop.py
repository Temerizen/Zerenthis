import json
import time
import traceback
from pathlib import Path
from datetime import datetime
import requests

from backend.proposal_engine import build_proposal, set_module_status, mark_proposal_status

BASE = Path(__file__).resolve().parents[1]
AUTO = BASE / "backend" / "data" / "autopilot"
RUNS = AUTO / "architect_runs.json"

BASE_URL = "https://semantiqai-backend-production-bcab.up.railway.app"
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
        "topic": "automated content factory for creators",
        "niche": "Content Monetization",
        "buyer": "Creators",
        "tone": "Premium",
        "promise": "produce more content faster",
        "bonus": "distribution templates",
        "notes": "roadmap execution: Content Factory"
    },
    "Video Engine": {
        "topic": "automated video engine for faceless content",
        "niche": "Content Monetization",
        "buyer": "Creators",
        "tone": "Premium",
        "promise": "publish videos faster",
        "bonus": "video hooks",
        "notes": "roadmap execution: Video Engine"
    },
    "Founder Console": {
        "topic": "founder control dashboard for AI operations",
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
    write_json(RUNS, data[-200:])

def verify_health():
    r = requests.get(f"{BASE_URL}/health", timeout=60)
    r.raise_for_status()
    data = r.json()
    return data.get("status") == "ok" or data.get("ok") is True

def execute_proposal(proposal):
    module = proposal["module"]
    risk = proposal.get("risk", "medium")

    if risk != "low":
        set_module_status(module, "blocked", {"blocked_reason": f"risk={risk} requires approval"})
        mark_proposal_status(proposal["id"], "blocked", {"blocked_reason": f"risk={risk} requires approval"})
        return {
            "status": "blocked",
            "reason": f"risk={risk} requires approval"
        }

    payload = MODULE_MAP.get(module)
    if not payload:
        set_module_status(module, "blocked", {"blocked_reason": "no execution mapping"})
        mark_proposal_status(proposal["id"], "blocked", {"blocked_reason": "no execution mapping"})
        return {
            "status": "blocked",
            "reason": "no execution mapping"
        }

    set_module_status(module, "building", {"started_at": now()})
    mark_proposal_status(proposal["id"], "building", {"started_at": now()})

    response = requests.post(
        f"{BASE_URL}/api/product-pack",
        json=payload,
        timeout=TIMEOUT
    )
    response.raise_for_status()
    result = response.json()

    health_ok = verify_health()
    success = bool(result) and health_ok

    if success:
        set_module_status(module, "complete", {
            "completed_at": now(),
            "last_result": "ok"
        })
        mark_proposal_status(proposal["id"], "complete", {
            "completed_at": now(),
            "result_summary": "executed and verified"
        })
        return {
            "status": "complete",
            "result": result,
            "verified": True
        }

    set_module_status(module, "blocked", {"blocked_reason": "verification failed"})
    mark_proposal_status(proposal["id"], "blocked", {"blocked_reason": "verification failed"})
    return {
        "status": "blocked",
        "reason": "verification failed",
        "result": result
    }

def loop():
    while True:
        try:
            proposal = build_proposal()
            print("=== ARCHITECT PROPOSAL ===")
            print(json.dumps(proposal, indent=2, ensure_ascii=False))

            if proposal.get("status") == "complete":
                append_run({
                    "time": now(),
                    "status": "complete",
                    "proposal": proposal
                })
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

