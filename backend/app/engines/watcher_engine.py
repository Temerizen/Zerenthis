import json
from pathlib import Path
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "backend" / "data"
BUILDER_DIR = DATA_DIR / "builder"
AUTOPILOT_DIR = DATA_DIR / "autopilot"

PROPOSALS_FILE = BUILDER_DIR / "proposals.json"
SAFE_ZONES_FILE = BUILDER_DIR / "safe_zones.json"
WATCHER_LOG_FILE = AUTOPILOT_DIR / "watcher_log.json"

AUTOPILOT_DIR.mkdir(parents=True, exist_ok=True)

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

def evaluate(proposal, safe_zones):
    target = proposal.get("target", "")
    risk = proposal.get("risk", "medium")

    requires = safe_zones.get("requires_founder_approval", [])
    blocked = safe_zones.get("blocked_prefixes", [])

    for b in blocked:
        if target.startswith(b):
            return "blocked", f"blocked prefix: {b}"

    if any(req in target for req in requires):
        return "needs_founder_approval", "touches protected target"

    if risk == "low":
        return "approved", "low risk auto-approved"

    if risk == "medium":
        return "queued_for_review", "medium risk held for watcher review"

    return "needs_founder_approval", "high risk change"

def run(payload):
    proposals = load_json(PROPOSALS_FILE, [])
    safe_zones = load_json(SAFE_ZONES_FILE, {})
    watcher_log = load_json(WATCHER_LOG_FILE, [])

    updated = []
    for p in proposals:
        if p.get("status") != "proposed":
            continue

        decision, reason = evaluate(p, safe_zones)
        p["status"] = decision
        p["watcher_reason"] = reason
        p["watched_at"] = datetime.now(timezone.utc).isoformat()

        watcher_log.append({
            "proposal_id": p.get("id"),
            "title": p.get("title"),
            "decision": decision,
            "reason": reason,
            "time": p["watched_at"]
        })
        updated.append(p)

    save_json(PROPOSALS_FILE, proposals)
    save_json(WATCHER_LOG_FILE, watcher_log)

    return {
        "status": "watcher_complete",
        "updated_count": len(updated),
        "updated": updated,
        "watcher_log": str(WATCHER_LOG_FILE)
    }
