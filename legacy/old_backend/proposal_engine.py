import json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parents[1]
DATA = Path("/data") if Path("/data").exists() else BASE / "backend" / "data"
CORE = DATA / "core"
AUTO = DATA / "autopilot"

ROADMAP = CORE / "roadmap.json"
PROPOSALS = AUTO / "proposals.json"

def now():
    return datetime.utcnow().isoformat()

def read_json(path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_completed_names():
    data = read_json(ROADMAP, {"modules": []})
    completed = set()
    for m in data.get("modules", []):
        if str(m.get("status", "")).lower() == "complete":
            completed.add(str(m.get("name", "")).strip())
    return completed

def choose_next_module():
    data = read_json(ROADMAP, {"modules": []})
    modules = data.get("modules", [])
    completed_names = get_completed_names()

    seen = set()
    for m in modules:
        name = str(m.get("name", "")).strip()
        status = str(m.get("status", "")).strip().lower()

        if not name or name in seen:
            continue
        seen.add(name)

        if name in completed_names:
            continue

        if status in ("pending", "planned", "proposed", "blocked", "building"):
            return m

    return None

def set_module_status(name, status, extra=None):
    data = read_json(ROADMAP, {"modules": []})
    changed = False
    for m in data.get("modules", []):
        if str(m.get("name", "")).strip() == str(name).strip():
            m["status"] = status
            if extra:
                m.update(extra)
            changed = True

    if not changed:
        data.setdefault("modules", []).append({
            "name": name,
            "status": status,
            **(extra or {})
        })

    write_json(ROADMAP, data)

def build_proposal():
    module = choose_next_module()
    if not module:
        return {"status": "complete", "message": "all modules processed"}

    name = str(module["name"]).strip()
    risk = module.get("risk", "medium")

    proposal = {
        "id": f"proposal_{name.lower().replace(' ', '_')}",
        "time": now(),
        "module": name,
        "risk": risk,
        "status": "proposed",
        "summary": f"Build next safe milestone for {name}",
        "changes": [
            {
                "type": "route_or_module",
                "target": f"{name.lower().replace(' ', '_')}",
                "reason": f"Advance roadmap for {name}"
            }
        ],
        "verification": [
            "health endpoint passes",
            "response shape is valid",
            "no startup errors"
        ]
    }

    proposals = read_json(PROPOSALS, [])
    if not isinstance(proposals, list):
        proposals = []
    proposals.append(proposal)
    write_json(PROPOSALS, proposals[-200:])

    set_module_status(name, "proposed", {"last_proposal_id": proposal["id"]})
    return proposal

def mark_proposal_status(proposal_id, status, extra=None):
    proposals = read_json(PROPOSALS, [])
    if not isinstance(proposals, list):
        proposals = []
    for p in proposals:
        if p.get("id") == proposal_id:
            p["status"] = status
            if extra:
                p.update(extra)
    write_json(PROPOSALS, proposals[-200:])

if __name__ == "__main__":
    print(json.dumps(build_proposal(), indent=2))
