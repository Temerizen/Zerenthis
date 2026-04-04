import json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "backend" / "data"
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
    with open(path, "w", encoding="utf-8-sig") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def choose_next_module():
    data = read_json(ROADMAP, {"modules": []})
    for m in data.get("modules", []):
        if m.get("status") in ("pending", "planned"):
            return m
    return None

def build_proposal():
    module = choose_next_module()
    if not module:
        return {"status": "complete", "message": "all modules processed"}

    name = module["name"]
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
            "new route/module imports cleanly",
            "response shape is valid",
            "no startup errors"
        ]
    }

    proposals = read_json(PROPOSALS, [])
    if not isinstance(proposals, list):
        proposals = []
    proposals.append(proposal)
    write_json(PROPOSALS, proposals[-200:])

    data = read_json(ROADMAP, {"modules": []})
    for m in data.get("modules", []):
        if m.get("name") == name:
            m["status"] = "planned"
    write_json(ROADMAP, data)

    return proposal

if __name__ == "__main__":
    print(json.dumps(build_proposal(), indent=2))

