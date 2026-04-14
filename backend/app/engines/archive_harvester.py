import json
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "backend" / "data"
GRAVE = DATA / "graveyard"
BUILDER = DATA / "builder"
PROPOSALS = BUILDER / "proposals.json"

def load(p, d): 
    try:
        return json.loads(p.read_text()) if p.exists() else d
    except:
        return d

def save(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=2))

def run(payload):
    proposals = load(PROPOSALS, [])
    files = list(GRAVE.glob("*.json"))

    created = []
    for f in files:
        try:
            data = json.loads(f.read_text())
            title = data.get("title") or f.stem

            proposal = {
                "id": uuid4().hex,
                "title": f"Recovered: {title}",
                "kind": "recovery",
                "target": "graveyard",
                "summary": "Recovered legacy idea",
                "priority": "medium",
                "risk": "low",
                "status": "proposed",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "source": "harvester"
            }
            proposals.append(proposal)
            created.append(proposal)
        except:
            continue

    save(PROPOSALS, proposals)

    return {
        "status": "harvest_complete",
        "created": len(created)
    }
