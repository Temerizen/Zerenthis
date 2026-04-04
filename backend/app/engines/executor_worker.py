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
    file_path = task.get("file_path")
    content = task.get("content", "")

    if not file_path:
        return {"applied": False, "reason": "no file_path"}

    path = ROOT / file_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

    return {"applied": True, "file": str(path)}

def run(payload):
    queue = load()
    processed = []

    for task in queue:
        if task.get("status") != "queued":
            continue

        try:
            result = write_file(task)
            task["status"] = "completed"
            task["result"] = result
            task["time"] = datetime.utcnow().isoformat()
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)

        processed.append(task)

    save(queue)

    return {
        "status": "executor_ran",
        "processed": len(processed)
    }
