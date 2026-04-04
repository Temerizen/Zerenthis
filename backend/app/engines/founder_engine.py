from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "backend" / "data"

JOB_FILE = DATA_DIR / "jobs.json"
WINNERS_FILE = DATA_DIR / "autopilot" / "winners.json"

def safe_load(p):
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text())
    except:
        return []

def run(payload):
    jobs = safe_load(JOB_FILE)
    winners = safe_load(WINNERS_FILE)

    return {
        "system": "Zerenthis Founder Core",
        "jobs_count": len(jobs),
        "winners_count": len(winners),
        "status": "operational",
        "next_actions": [
            "Generate Product Pack",
            "Run Evolution",
            "View Winners",
            "Deploy Content"
        ]
    }