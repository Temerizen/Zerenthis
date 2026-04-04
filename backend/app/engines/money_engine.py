import json, random
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "backend" / "data"
AUTO_DIR = DATA_DIR / "autopilot"

JOBS_FILE = DATA_DIR / "jobs.json"
WINNERS_FILE = AUTO_DIR / "winners.json"

def load_json(p, default):
    try:
        if p.exists():
            return json.loads(p.read_text())
    except:
        pass
    return default

def save_json(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))

IDEAS = [
    "Faceless TikTok niche domination pack",
    "AI-powered side hustle starter kit",
    "Beginner YouTube automation system",
    "Instagram reels growth engine",
    "Digital product blueprint",
]

def score(title):
    s = 0
    if "AI" in title: s += 2
    if "TikTok" in title or "Reels" in title: s += 2
    s += random.randint(1,5)
    return s

def run(payload):
    jobs = load_json(JOBS_FILE, [])
    winners = load_json(WINNERS_FILE, [])

    idea = random.choice(IDEAS)
    s = score(idea)

    job = {
        "id": uuid4().hex,
        "title": idea,
        "score": s,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    jobs.append(job)
    if s >= 6:
        winners.append(job)

    save_json(JOBS_FILE, jobs)
    save_json(WINNERS_FILE, winners)

    return {
        "idea": idea,
        "score": s,
        "is_winner": s >= 6,
        "jobs": len(jobs),
        "winners": len(winners)
    }