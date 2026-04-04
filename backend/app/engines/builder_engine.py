import json, uuid
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "backend" / "data"
PROPOSALS = DATA / "builder" / "proposals.json"
QUEUE = DATA / "execution" / "queue.json"

def load(p):
    try: return json.loads(p.read_text())
    except: return []

def save(p,d):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d,indent=2))

def run(payload):
    proposals = load(PROPOSALS)
    queue = load(QUEUE)

    created = []

    for i in range(3):
        pid = uuid.uuid4().hex

        file_path = f"backend/app/generated/module_{pid}.py"

        content = f"""# Auto Module
def run():
    return "Module {pid} alive"
"""

        task = {
            "id": pid,
            "kind": "create_file",
            "file_path": file_path,
            "content": content,
            "status": "queued",
            "created_at": datetime.utcnow().isoformat()
        }

        proposals.append(task)
        queue.append(task)
        created.append(task)

    save(PROPOSALS, proposals)
    save(QUEUE, queue)

    return {"status":"built","created":len(created)}
