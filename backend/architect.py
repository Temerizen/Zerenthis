import json, random
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "backend" / "data"

ROADMAP = DATA / "core" / "roadmap.json"
PLAN = DATA / "autopilot" / "architect_plan.json"

def now():
    return datetime.utcnow().isoformat()

def load():
    return json.load(open(ROADMAP, "r"))

def save(data):
    json.dump(data, open(ROADMAP, "w"), indent=2)

def choose_module(modules):
    pending = [m for m in modules if m["status"] != "complete"]
    return random.choice(pending) if pending else None

def build_plan():
    data = load()
    module = choose_module(data["modules"])

    if not module:
        return {"status": "complete"}

    module["status"] = "building"
    save(data)

    plan = {
        "time": now(),
        "module": module["name"],
        "task": f"Build core functionality for {module['name']}",
        "priority": "high"
    }

    json.dump(plan, open(PLAN, "w"), indent=2)
    return plan

def complete_module(name):
    data = load()
    for m in data["modules"]:
        if m["name"] == name:
            m["status"] = "complete"
    save(data)
