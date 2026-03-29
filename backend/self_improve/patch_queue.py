import json
import uuid
from pathlib import Path

BASE = Path("backend/self_improve")
BASE.mkdir(parents=True, exist_ok=True)

QUEUE_FILE = BASE / "queue.json"


def load_queue():
    if not QUEUE_FILE.exists():
        return []
    try:
        return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_queue(queue):
    QUEUE_FILE.write_text(json.dumps(queue, indent=2), encoding="utf-8")


def add_patch(patch):
    queue = load_queue()
    patch["id"] = str(uuid.uuid4())
    patch["status"] = "pending"
    queue.append(patch)
    save_queue(queue)
    return patch["id"]


def get_pending():
    return [p for p in load_queue() if p.get("status") == "pending"]


def mark_status(patch_id, status):
    queue = load_queue()
    for patch in queue:
        if patch.get("id") == patch_id:
            patch["status"] = status
    save_queue(queue)
