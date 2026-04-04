import json
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "backend" / "data"
BUILDER_DIR = DATA_DIR / "builder"
EXEC_DIR = DATA_DIR / "execution"

PROPOSALS_FILE = BUILDER_DIR / "proposals.json"
QUEUE_FILE = EXEC_DIR / "queue.json"

BUILDER_DIR.mkdir(parents=True, exist_ok=True)
EXEC_DIR.mkdir(parents=True, exist_ok=True)

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

def run(payload):
    proposals = load_json(PROPOSALS_FILE, [])
    queue = load_json(QUEUE_FILE, [])

    existing_ids = {item.get("proposal_id") for item in queue}
    created = []

    for p in proposals:
        if p.get("status") != "approved":
            continue
        if p.get("id") in existing_ids:
            continue

        task = {
            "id": uuid4().hex,
            "proposal_id": p.get("id"),
            "title": p.get("title"),
            "kind": p.get("kind"),
            "target": p.get("target"),
            "summary": p.get("summary"),
            "priority": p.get("priority", "medium"),
            "status": "queued",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": "execution_engine"
        }
        queue.append(task)
        created.append(task)

    save_json(QUEUE_FILE, queue)

    return {
        "status": "execution_queue_updated",
        "queued_now": len(created),
        "total_queued": len(queue),
        "created": created,
        "queue_file": str(QUEUE_FILE)
    }