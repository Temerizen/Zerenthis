from __future__ import annotations
import json, time, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "backend" / "data" / "self_improver"
BACKUPS = DATA / "backups"
FILE = DATA / "proposals.json"

DATA.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(parents=True, exist_ok=True)

PROTECTED = [".env", ".git", "node_modules", "venv", "backend/data"]

def load():
    if not FILE.exists():
        return []
    return json.loads(FILE.read_text())

def save(d):
    FILE.write_text(json.dumps(d, indent=2))

def new_id():
    return f"prop_{int(time.time())}"

def propose(title, reason, steps):
    p = {
        "id": new_id(),
        "title": title,
        "reason": reason,
        "steps": steps,
        "status": "pending"
    }
    d = load()
    d.append(p)
    save(d)
    return p

def approve(pid):
    d = load()
    found = False
    for x in d:
        if x["id"] == pid:
            x["status"] = "approved"
            found = True
    save(d)
    return found

def reject(pid):
    d = load()
    found = False
    for x in d:
        if x["id"] == pid:
            x["status"] = "rejected"
            found = True
    save(d)
    return found

def backup(path):
    if not path.exists():
        return None
    b = BACKUPS / f"{int(time.time())}_{path.name}.bak"
    shutil.copy2(path, b)
    return b

def execute(pid):
    d = load()
    p = next((x for x in d if x["id"] == pid), None)

    if not p or p["status"] != "approved":
        return {"error": "not approved"}

    backups = []

    try:
        for s in p["steps"]:
            path = ROOT / s["path"]

            if any(x in s["path"] for x in PROTECTED):
                raise Exception("blocked path")

            if s["action"] == "create_file":
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(s.get("content", ""))

            elif s["action"] == "edit_file":
                b = backup(path)
                if b:
                    backups.append((path, b))
                txt = path.read_text()
                txt = txt.replace(s["find"], s["replace"])
                path.write_text(txt)

            elif s["action"] == "delete_file":
                b = backup(path)
                if b:
                    backups.append((path, b))
                path.unlink()

        p["status"] = "applied"
        save(d)
        return {"ok": True, "id": pid}

    except Exception as e:
        for orig, b in backups:
            shutil.copy2(b, orig)
        p["status"] = "failed"
        save(d)
        return {"ok": False, "id": pid, "error": str(e)}

def pending():
    return [x for x in load() if x["status"] == "pending"]

def verify():
    return True
