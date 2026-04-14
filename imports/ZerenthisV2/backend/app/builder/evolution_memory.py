import os, json, time
from typing import Dict, List

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DATA_DIR = os.path.join(BASE_DIR, "backend/data")
os.makedirs(DATA_DIR, exist_ok=True)

MEMORY_FILE = os.path.join(DATA_DIR, "builder_memory.json")

def _load():
    if not os.path.exists(MEMORY_FILE):
        return {"runs": [], "stats": {"accepted": 0, "rejected": 0}}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {"runs": [], "stats": {"accepted": 0, "rejected": 0}}

def _save(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def record(run: Dict):
    data = _load()
    data["runs"].append(run)
    if run.get("status") == "applied":
        data["stats"]["accepted"] += 1
    else:
        data["stats"]["rejected"] += 1
    # keep memory bounded
    data["runs"] = data["runs"][-200:]
    _save(data)

def stats():
    return _load().get("stats", {})

def last_runs(n: int = 10) -> List[Dict]:
    return _load().get("runs", [])[-n:]
