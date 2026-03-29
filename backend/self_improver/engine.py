from __future__ import annotations
import json, time, shutil, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "backend" / "data" / "self_improver"
BACKUPS = DATA / "backups"
FILE = DATA / "proposals.json"

DATA.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(parents=True, exist_ok=True)

PROTECTED = {".env",".git","node_modules","venv","backend/data"}

def load():
    if not FILE.exists():
        return []
    try:
        return json.loads(FILE.read_text(encoding="utf-8"))
    except:
        return []

def save(d):
    FILE.write_text(json.dumps(d, indent=2), encoding="utf-8")

def new_id():
    return f"prop_{int(time.time())}_{uuid.uuid4().hex[:6]}"

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

def pending():
    return [x for x in load() if x.get("status") == "pending"]

def approve(pid):
    d = load()
    for x in d:
        if x["id"] == pid:
            x["status"] = "approved"
    save(d)

def reject(pid):
    d = load()
    for x in d:
        if x["id"] == pid:
            x["status"] = "rejected"
    save(d)

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
                raise Exception("blocked")

            if s["action"] == "create_file":
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(s.get("content",""))

            elif s["action"] == "edit_file":
                b = backup(path)
                if b:
                    backups.append((path,b))
                txt = path.read_text()
                if s["find"] not in txt:
                    raise Exception(f"find text not found in {s['path']}")
                txt = txt.replace(s["find"], s["replace"], 1)
                path.write_text(txt)

            elif s["action"] == "delete_file":
                b = backup(path)
                if b:
                    backups.append((path,b))
                path.unlink()

        p["status"] = "applied"
        save(d)
        return {"ok": True}

    except Exception as e:
        for orig,b in backups:
            shutil.copy2(b,orig)
        p["status"] = "failed"
        save(d)
        return {"error": str(e)}
