from fastapi import APIRouter
from pathlib import Path
import json, random
from datetime import datetime

router = APIRouter()

DATA_DIR = Path("/data") if Path("/data").exists() else Path("backend/data")
WINNERS_FILE = DATA_DIR / "autopilot/winners.json"

def read_winners():
    if WINNERS_FILE.exists():
        try:
            return json.loads(WINNERS_FILE.read_text())
        except:
            return []
    return []

def pick_dominant_pattern(winners):
    if not winners:
        return {"niche":"Content Monetization","buyer":"Creators"}

    niche_count = {}
    buyer_count = {}

    for w in winners:
        p = w.get("payload",{})
        niche = p.get("niche","")
        buyer = p.get("buyer","")

        niche_count[niche] = niche_count.get(niche,0)+1
        buyer_count[buyer] = buyer_count.get(buyer,0)+1

    top_niche = max(niche_count, key=niche_count.get)
    top_buyer = max(buyer_count, key=buyer_count.get)

    return {"niche": top_niche, "buyer": top_buyer}

@router.post("/api/evolution/run")
def aggressive_evolution():
    winners = read_winners()
    pattern = pick_dominant_pattern(winners)

    modules_priority = [
        "Content Factory",
        "Video Engine",
        "Money Engine"
    ]

    jobs = []

    for module in modules_priority:
        jobs.append({
            "topic": f"Advanced {module} system for {pattern['buyer']}",
            "niche": pattern["niche"],
            "tone": "Premium",
            "buyer": pattern["buyer"],
            "promise": "increase output and revenue faster",
            "notes": f"Aggressive evolution targeting {module}"
        })

    return {
        "ok": True,
        "mode": "AGGRESSIVE",
        "pattern": pattern,
        "jobs_created": jobs
    }

