from __future__ import annotations
import json, time
from pathlib import Path
from typing import Dict, Any

PATH = Path("backend/data/meta_intelligence.json")

def _load():
    if not PATH.exists():
        return {"preferences": {}, "history": []}
    try:
        return json.loads(PATH.read_text())
    except:
        return {"preferences": {}, "history": []}

def _save(d):
    PATH.parent.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(d, indent=2))

def run(signal: Dict[str, Any]):
    d = _load()
    d["history"].append({"t": time.time(), "signal": signal})
    d["history"] = d["history"][-100:]
    _save(d)
    return {"status":"ok","history":len(d["history"])}
