import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "backend" / "data"
QUEUE = DATA / "execution" / "queue.json"

def load():
    try:
        return json.loads(QUEUE.read_text())
    except:
        return []

def save(data):
    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE.write_text(json.dumps(data, indent=2))

def write_file(task):
    path = ROOT / task.get("file_path")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(task.get("content",""), encoding="utf-8")
    return {"applied": True, "file": str(path)}

def run(payload):
    queue = load()
    updated = []

    for t in queue:
        if t.get("status") != "queued":
            continue

        try:
            res = write_file(t)
            t["status"] = "completed"
            t["result"] = res
            t["time"] = datetime.utcnow().isoformat()
        except Exception as e:
            t["status"] = "failed"
            t["error"] = str(e)

        updated.append(t)

    save(queue)

    return {"status":"executed","count":len(updated)}
