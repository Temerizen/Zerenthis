import os
import time
import json
import random
import traceback
from datetime import datetime, timezone

import requests

BASE_URL = os.getenv("BASE_URL", "https://zerenthis-production.up.railway.app").rstrip("/")
INTERVAL = int(os.getenv("AUTOPILOT_INTERVAL_SECONDS", "900"))
TITLE_PREFIX = os.getenv("AUTOPILOT_TITLE_PREFIX", "Autopilot")
TIMEOUT = int(os.getenv("AUTOPILOT_TIMEOUT_SECONDS", "120"))
LOG_DIR = os.getenv("AUTOPILOT_LOG_DIR", "backend/data/autopilot")
ENABLED = os.getenv("AUTOPILOT_ENABLED", "true").lower() in {"1", "true", "yes", "on"}

PROMPTS = [
    {
        "title": "AI Productivity Guide",
        "prompt": "Build a workflow for generating and selling a premium AI productivity guide for busy entrepreneurs who want to automate content and income."
    },
    {
        "title": "Faceless Content Blueprint",
        "prompt": "Build a workflow for generating and selling a faceless content monetization blueprint for creators who want fast automated output."
    },
    {
        "title": "YouTube Automation Offer",
        "prompt": "Build a workflow for generating and selling a premium YouTube automation starter offer for beginners who want practical templates and immediate momentum."
    },
    {
        "title": "Digital Product Funnel",
        "prompt": "Build a workflow for generating and selling a premium digital product funnel guide for solo founders using AI."
    }
]

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def write_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def post_json(path: str, payload: dict) -> dict:
    url = f"{BASE_URL}{path}"
    r = requests.post(url, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def run_once() -> dict:
    chosen = random.choice(PROMPTS)
    build_payload = {
        "title": f"{TITLE_PREFIX} - {chosen['title']}",
        "prompt": chosen["prompt"]
    }
    build = post_json("/api/workflow/build", build_payload)
    workflow = build.get("workflow", {})
    workflow_id = workflow.get("id")
    if not workflow_id:
        raise RuntimeError(f"No workflow id returned: {build}")
    run = post_json("/api/workflow/run", {"workflow_id": workflow_id})
    return {
        "time": now_iso(),
        "build_payload": build_payload,
        "build_response": build,
        "run_response": run
    }

def main() -> None:
    ensure_dir(LOG_DIR)
    print(f"[autopilot] enabled={ENABLED} base_url={BASE_URL} interval={INTERVAL}s")
    if not ENABLED:
        print("[autopilot] disabled by AUTOPILOT_ENABLED")
        return

    while True:
        started = now_iso()
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        try:
            print(f"[autopilot] cycle start {started}")
            result = run_once()
            out = os.path.join(LOG_DIR, f"autopilot_run_{stamp}.json")
            write_json(out, result)
            run_status = result.get("run_response", {}).get("run", {}).get("status")
            print(f"[autopilot] cycle complete status={run_status} log={out}")
        except Exception as e:
            err = {
                "time": now_iso(),
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            out = os.path.join(LOG_DIR, f"autopilot_error_{stamp}.json")
            write_json(out, err)
            print(f"[autopilot] cycle failed log={out}")
            print(err["traceback"])
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()