import json, os, time

DATA_PATH = "backend/data/pattern_memory.json"
DECAY_PER_HOUR = 0.15
MIN_WEIGHT = 0.25

def _load():
    if not os.path.exists(DATA_PATH):
        return {"patterns": []}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _apply_decay(pattern):
    now = time.time()
    last_seen = pattern.get("last_seen", pattern.get("timestamp", now))
    hours_old = max((now - last_seen) / 3600, 0)
    current_weight = float(pattern.get("weight", 1.0))
    decayed_weight = max(current_weight - (hours_old * DECAY_PER_HOUR), 0)
    pattern["weight"] = round(decayed_weight, 3)
    pattern["hours_old"] = round(hours_old, 3)
    return pattern

def extract_pattern(thought_chain):
    if not thought_chain:
        return None

    focuses = [t.get("focus") for t in thought_chain if isinstance(t, dict) and t.get("focus")]
    if len(focuses) < 3:
        return None

    last = focuses[-3:]

    if len(set(last)) == 1:
        return {
            "type": "repetition",
            "focus": last[0],
            "signature": f"repetition::{last[0]}"
        }

    return {
        "type": "variation",
        "sequence": last,
        "signature": "variation::" + "->".join(last)
    }

def _merge_pattern(existing, new_pattern):
    existing["count"] = existing.get("count", 1) + 1
    existing["last_seen"] = time.time()
    existing["weight"] = round(min(existing.get("weight", 1.0) + 0.5, 10.0), 3)

    if new_pattern.get("type") == "repetition":
        existing["focus"] = new_pattern.get("focus")

    if new_pattern.get("type") == "variation":
        existing["sequence"] = new_pattern.get("sequence", [])

    return existing

def decay_pattern_memory():
    data = _load()
    patterns = data.get("patterns", [])

    decayed = []
    removed = 0

    for pattern in patterns:
        updated = _apply_decay(pattern)
        if updated.get("weight", 0) >= MIN_WEIGHT:
            decayed.append(updated)
        else:
            removed += 1

    decayed.sort(key=lambda p: (p.get("weight", 0), p.get("last_seen", 0)), reverse=True)
    data["patterns"] = decayed[:50]
    _save(data)

    return {
        "status": "decay_applied",
        "remaining": len(data["patterns"]),
        "removed": removed,
        "top_patterns": data["patterns"][:5]
    }

def update_pattern_memory(thought_chain):
    data = _load()
    patterns = data.get("patterns", [])
    pattern = extract_pattern(thought_chain)

    if not pattern:
        return {"status": "no_pattern"}

    now = time.time()
    pattern["timestamp"] = now
    pattern["last_seen"] = now
    pattern["count"] = 1
    pattern["weight"] = 1.0

    merged = False
    for existing in patterns:
        if existing.get("signature") == pattern.get("signature"):
            _merge_pattern(existing, pattern)
            merged = True
            pattern = existing
            break

    if not merged:
        patterns.append(pattern)

    patterns.sort(key=lambda p: (p.get("weight", 0), p.get("last_seen", 0)), reverse=True)
    data["patterns"] = patterns[:50]
    _save(data)

    return {
        "status": "pattern_recorded",
        "pattern": pattern,
        "top_patterns": data["patterns"][:5],
        "total_patterns": len(data["patterns"])
    }
