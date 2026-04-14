from __future__ import annotations
import json, time
from pathlib import Path

PATH = Path("backend/data/world_state.json")

def _load():
    if not PATH.exists():
        return {"entities":{}, "signals":[]}
    try:
        return json.loads(PATH.read_text())
    except:
        return {"entities":{}, "signals":[]}

def _save(d):
    PATH.parent.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(d, indent=2))

def update(payload):
    d = _load()
    d["signals"].append({"t":time.time(),"data":payload})
    d["signals"]=d["signals"][-200:]
    _save(d)
    return {"status":"ok","signals":len(d["signals"])}

def state():
    return _load()
