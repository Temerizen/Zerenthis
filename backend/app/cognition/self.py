from __future__ import annotations
import json, time
from pathlib import Path

PATH = Path("backend/data/self_model.json")

def _default():
    return {"actions": 0, "success": 0}

def _load():
    if not PATH.exists():
        return _default()
    try:
        d = json.loads(PATH.read_text())

        # --- MIGRATION LOGIC ---
        if "actions" not in d:
            # convert old structure → new structure
            perf = d.get("performance", {})
            total = perf.get("total_actions", 0)
            success = perf.get("successful_actions", 0)

            return {
                "actions": total,
                "success": success
            }

        return d
    except:
        return _default()

def _save(d):
    PATH.parent.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(d, indent=2))

def update(payload):
    d = _load()
    d["actions"] += 1
    if payload.get("result") == "ok":
        d["success"] += 1
    d["rate"] = d["success"] / d["actions"]
    _save(d)
    return d

def state():
    return _load()
