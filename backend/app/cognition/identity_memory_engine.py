import json, os, time

IDENTITY_PATH = "backend/data/identity_consolidation.json"
MEMORY_PATH = "backend/data/identity_memory.json"

def _safe_load(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        return default

def _safe_save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def run():
    identity = _safe_load(IDENTITY_PATH, {})
    memory = _safe_load(MEMORY_PATH, {
        "baseline_traits": {
            "caution": 0.5,
            "adaptability": 0.5,
            "confidence": 0.5,
            "persistence": 0.5
        },
        "history": []
    })

    current = identity.get("traits", {})
    baseline = memory.get("baseline_traits", {})

    updated = {}

    for k in ["caution", "adaptability", "confidence", "persistence"]:
        cur = current.get(k, 0.5)
        base = baseline.get(k, 0.5)
        new_val = (base * 0.8) + (cur * 0.2)
        updated[k] = round(new_val, 4)

    record = {
        "timestamp": time.time(),
        "traits": current
    }

    memory["history"].append(record)
    memory["history"] = memory["history"][-200:]
    memory["baseline_traits"] = updated

    _safe_save(MEMORY_PATH, memory)

    return {
        "status": "identity_memory_updated",
        "baseline_traits": updated,
        "history_size": len(memory["history"])
    }
