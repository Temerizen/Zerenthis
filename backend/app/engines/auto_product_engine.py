import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "backend" / "data"
AUTO = DATA / "autopilot"
WINNERS = AUTO / "winners.json"

def load(p, d):
    try:
        return json.loads(p.read_text()) if p.exists() else d
    except:
        return d

def run(payload):
    winners = load(WINNERS, [])
    created = []

    for w in winners[-3:]:
        created.append({
            "topic": w.get("idea", {}).get("title", "Auto Product"),
            "niche": w.get("idea", {}).get("niche", "General")
        })

    return {
        "status": "auto_products_ready",
        "to_build": created
    }
