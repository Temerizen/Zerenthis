from __future__ import annotations

import json
import time
import shutil
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "backend" / "data" / "self_improver"
BACKUPS = DATA / "backups"
FILE = DATA / "proposals.json"
EXECUTION_LOG = DATA / "execution_log.json"

DATA.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(parents=True, exist_ok=True)

PROTECTED_TOKENS = [".env", ".git", "node_modules", "venv", "backend/data"]

def load():
    if not FILE.exists():
        return []
    try:
        data = json.loads(FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def save(d):
    FILE.write_text(json.dumps(d, indent=2), encoding="utf-8")

def _load_execution_log():
    if not EXECUTION_LOG.exists():
        return []
    try:
        data = json.loads(EXECUTION_LOG.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def _save_execution_log(items):
    EXECUTION_LOG.write_text(json.dumps(items, indent=2), encoding="utf-8")

def new_id():
    return f"prop_{int(time.time())}_{uuid.uuid4().hex[:6]}"

def propose(title, reason, steps, meta=None):
    p = {
        "id": new_id(),
        "title": title,
        "reason": reason,
        "steps": steps,
        "status": "pending",
        "meta": meta or {},
        "created_ts": time.time(),
    }
    d = load()
    d.append(p)
    save(d)
    return p

def pending():
    return [x for x in load() if x.get("status") == "pending"]

def approved():
    return [x for x in load() if x.get("status") == "approved"]

def applied():
    return [x for x in load() if x.get("status") == "applied"]

def failed():
    return [x for x in load() if x.get("status") == "failed"]

def approve(pid):
    d = load()
    matches = [x for x in d if x.get("id") == pid]
    if not matches:
        return False
    latest = sorted(matches, key=lambda x: float(x.get("created_ts", 0) or 0))[-1]
    latest["status"] = "approved"
    latest["approved_ts"] = time.time()
    save(d)
    return True

def reject(pid):
    d = load()
    matches = [x for x in d if x.get("id") == pid]
    if not matches:
        return False
    latest = sorted(matches, key=lambda x: float(x.get("created_ts", 0) or 0))[-1]
    latest["status"] = "rejected"
    latest["rejected_ts"] = time.time()
    save(d)
    return True

def backup(path: Path):
    if not path.exists():
        return None
    b = BACKUPS / f"{int(time.time())}_{uuid.uuid4().hex[:6]}_{path.name}.bak"
    shutil.copy2(path, b)
    return b

def _blocked(path_str: str) -> bool:
    normalized = path_str.replace("\\", "/").lower()
    return any(token.lower() in normalized for token in PROTECTED_TOKENS)

def execute(pid):
    d = load()
    matches = [x for x in d if x.get("id") == pid]
    if not matches:
        return {"error": "not approved"}

    p = sorted(matches, key=lambda x: float(x.get("created_ts", 0) or 0))[-1]
    if p.get("status") != "approved":
        return {"error": "not approved"}

    backups = []
    created = []
    started_at = int(time.time())
    execution_log = _load_execution_log()

    try:
        for s in p.get("steps", []):
            path_str = str(s.get("path", ""))
            if not path_str:
                raise Exception("missing path")
            if _blocked(path_str):
                raise Exception(f"blocked path: {path_str}")

            path = ROOT / path_str
            action = s.get("action")

            if action == "create_file":
                if path.exists():
                    raise Exception(f"file already exists: {path_str}")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(s.get("content", ""), encoding="utf-8")
                created.append(path)

            elif action == "edit_file":
                if not path.exists():
                    raise Exception(f"file missing: {path_str}")
                b = backup(path)
                if b:
                    backups.append((path, b))
                txt = path.read_text(encoding="utf-8", errors="ignore")
                find = s.get("find", "")
                replace = s.get("replace", "")
                if find not in txt:
                    raise Exception(f"find text not found in {path_str}")
                txt = txt.replace(find, replace, 1)
                path.write_text(txt, encoding="utf-8")

            elif action == "delete_file":
                if not path.exists():
                    raise Exception(f"file missing: {path_str}")
                b = backup(path)
                if b:
                    backups.append((path, b))
                path.unlink()

            else:
                raise Exception(f"unknown action: {action}")

        finished = int(time.time())
        p["status"] = "applied"
        p["applied_ts"] = finished
        save(d)

        execution_log.append({
            "id": pid,
            "title": p.get("title"),
            "status": "applied",
            "started_at": started_at,
            "finished_at": finished,
            "steps": p.get("steps", []),
        })
        _save_execution_log(execution_log)
        return {"ok": True, "id": pid, "status": "applied"}

    except Exception as e:
        for path in reversed(created):
            try:
                if path.exists():
                    path.unlink()
            except Exception:
                pass

        for orig, b in reversed(backups):
            try:
                orig.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(b, orig)
            except Exception:
                pass

        p["status"] = "failed"
        p["failed_ts"] = int(time.time())
        p["error"] = str(e)
        save(d)

        execution_log.append({
            "id": pid,
            "title": p.get("title"),
            "status": "failed",
            "started_at": started_at,
            "finished_at": int(time.time()),
            "steps": p.get("steps", []),
            "error": str(e),
        })
        _save_execution_log(execution_log)
        return {"ok": False, "id": pid, "error": str(e)}

def verify():
    return True

