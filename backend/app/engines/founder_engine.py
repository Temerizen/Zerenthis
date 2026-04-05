import json
import os
from datetime import datetime, timezone

DATA_DIR = os.path.join("backend", "data")

def build_founder_snapshot() -> dict:
    now = datetime.now(timezone.utc).isoformat()
    modules = [
        "core",
        "money",
        "content",
        "school",
        "research",
        "cognitive",
        "genius"
    ]

    snapshot = {
        "generated_at": now,
        "status": "ok",
        "modules": [{"name": m, "status": "active"} for m in modules]
    }

    path = os.path.join(DATA_DIR, "founder_snapshot.json")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    return snapshot
