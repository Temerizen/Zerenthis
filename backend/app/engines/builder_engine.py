import json
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "backend" / "data"
BUILDER_DIR = DATA_DIR / "builder"

PROPOSALS_FILE = BUILDER_DIR / "proposals.json"
ROADMAP_FILE = BUILDER_DIR / "roadmap_backlog.json"
SAFE_ZONES_FILE = BUILDER_DIR / "safe_zones.json"

BUILDER_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_ROADMAP = [
    {"title":"Money Engine to Product Pipeline","kind":"pipeline","target":"money_engine -> product_engine","summary":"Turn scored ideas into built assets automatically","priority":"high"},
    {"title":"Winners to Product Auto-Build","kind":"automation","target":"winners","summary":"When a winner appears, queue a product build","priority":"high"},
    {"title":"Founder Dashboard Expansion","kind":"ui","target":"frontend/src/main.js","summary":"Add queue, proposals, approvals, outputs, health blocks","priority":"medium"},
    {"title":"Archive Harvester","kind":"recovery","target":"graveyards","summary":"Mine old project ideas and convert them into structured proposals","priority":"high"},
    {"title":"Video Content Asset Layer","kind":"engine","target":"content/video","summary":"Turn winning products into sellable content packages","priority":"medium"},
    {"title":"Autopilot Watcher Rules","kind":"supervision","target":"autopilot","summary":"Auto-approve low-risk changes and block dangerous ones","priority":"high"}
]

DEFAULT_SAFE_ZONES = {
    "allow_create": ["backend/app/engines", "backend/data", "frontend/src"],
    "allow_modify": ["backend/app/engines/engine_loader.py", "frontend/src/main.js", "frontend/src/api.js", "backend/app/routes/system_routes.py", "backend/app/main.py"],
    "blocked_prefixes": [".git", ".venv", "venv", "node_modules"],
    "requires_founder_approval": ["backend/app/main.py", "desktop/src/main.js", "Procfile", "railway.json", "package.json"]
}

def load_json(p, default):
    try:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except:
        pass
    return default

def save_json(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")

def ensure_seed_files():
    if not ROADMAP_FILE.exists():
        save_json(ROADMAP_FILE, DEFAULT_ROADMAP)
    if not SAFE_ZONES_FILE.exists():
        save_json(SAFE_ZONES_FILE, DEFAULT_SAFE_ZONES)
    if not PROPOSALS_FILE.exists():
        save_json(PROPOSALS_FILE, [])

def risk_for(item):
    title = (item.get("title") or "").lower()
    target = (item.get("target") or "").lower()
    kind = (item.get("kind") or "").lower()

    if "main.py" in target or "procfile" in target or "desktop" in target:
        return "high"
    if kind in ["supervision", "recovery", "pipeline", "automation"]:
        return "medium"
    return "low"

def run(payload):
    ensure_seed_files()

    backlog = load_json(ROADMAP_FILE, DEFAULT_ROADMAP)
    proposals = load_json(PROPOSALS_FILE, [])
    existing_titles = {p.get("title") for p in proposals}

    limit = int(payload.get("limit", 5))
    created = []

    for item in backlog:
        if len(created) >= limit:
            break
        if item.get("title") in existing_titles:
            continue

        proposal = {
            "id": uuid4().hex,
            "title": item.get("title"),
            "kind": item.get("kind"),
            "target": item.get("target"),
            "summary": item.get("summary"),
            "priority": item.get("priority", "medium"),
            "risk": risk_for(item),
            "status": "proposed",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": "roadmap_backlog"
        }
        proposals.append(proposal)
        created.append(proposal)

    save_json(PROPOSALS_FILE, proposals)

    return {
        "status": "proposals_created",
        "created_count": len(created),
        "created": created,
        "total_proposals": len(proposals),
        "proposal_store": str(PROPOSALS_FILE),
        "backlog_store": str(ROADMAP_FILE)
    }