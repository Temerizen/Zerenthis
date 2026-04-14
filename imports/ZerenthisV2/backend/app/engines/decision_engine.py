import json
from pathlib import Path
from backend.app.engines.target_engine import generate_targets

DATA_PATH = Path("backend/data/intelligence/current_topic.json")

def decide():
    targets = generate_targets()
    best = targets[0] if targets else None

    if best:
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(best, f, indent=2)

    return {
        "selected": best,
        "total_targets": len(targets)
    }

def get_current_topic():
    if DATA_PATH.exists():
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None
