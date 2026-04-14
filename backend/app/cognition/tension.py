import json, os, time

TENSION_PATH = "backend/data/tension_memory.json"
DECAY_PER_HOUR = 0.12
MIN_TENSION = 0.2

def _load():
    if not os.path.exists(TENSION_PATH):
        return {"tensions": []}
    with open(TENSION_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data):
    with open(TENSION_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _apply_decay(tension):
    now = time.time()
    last_seen = tension.get("last_seen", tension.get("timestamp", now))
    hours_old = max((now - last_seen) / 3600, 0)
    current_strength = float(tension.get("strength", 1.0))
    decayed = max(current_strength - (hours_old * DECAY_PER_HOUR), 0)
    tension["strength"] = round(decayed, 3)
    tension["hours_old"] = round(hours_old, 3)
    return tension

def decay_tension_memory():
    data = _load()
    tensions = data.get("tensions", [])

    kept = []
    removed = 0

    for tension in tensions:
        updated = _apply_decay(tension)
        if updated.get("strength", 0) >= MIN_TENSION:
            kept.append(updated)
        else:
            removed += 1

    kept.sort(key=lambda t: (t.get("strength", 0), t.get("last_seen", 0)), reverse=True)
    data["tensions"] = kept[:25]
    _save(data)

    return {
        "status": "tension_decay_applied",
        "remaining": len(data["tensions"]),
        "removed": removed,
        "top_tensions": data["tensions"][:5]
    }

def update_tension_memory(pattern_bias: dict | None = None):
    pattern_bias = pattern_bias or {}
    data = _load()
    tensions = data.get("tensions", [])

    if not pattern_bias.get("conflict"):
        return {
            "status": "no_conflict",
            "active_tensions": len(tensions)
        }

    winner = pattern_bias.get("winner", "unknown")
    reason = pattern_bias.get("reason", "unknown")
    weight = float(pattern_bias.get("weight", 0))
    opposing_weight = float(pattern_bias.get("opposing_weight", 0))
    gap = round(abs(weight - opposing_weight), 3)

    signature = f"{reason}::{winner}"

    now = time.time()
    found = None

    for tension in tensions:
        if tension.get("signature") == signature:
            found = tension
            break

    if found:
        found["count"] = found.get("count", 1) + 1
        found["last_seen"] = now
        found["winner"] = winner
        found["reason"] = reason
        found["gap"] = gap
        found["strength"] = round(min(found.get("strength", 1.0) + max(0.35, gap * 0.5), 10.0), 3)
    else:
        found = {
            "signature": signature,
            "winner": winner,
            "reason": reason,
            "gap": gap,
            "strength": round(max(1.0, gap), 3),
            "count": 1,
            "timestamp": now,
            "last_seen": now
        }
        tensions.append(found)

    tensions.sort(key=lambda t: (t.get("strength", 0), t.get("last_seen", 0)), reverse=True)
    data["tensions"] = tensions[:25]
    _save(data)

    return {
        "status": "tension_recorded",
        "tension": found,
        "top_tensions": data["tensions"][:5],
        "active_tensions": len(data["tensions"])
    }

def get_tension_bias():
    data = _load()
    tensions = data.get("tensions", [])

    if not tensions:
        return {
            "bias": None,
            "source": "no_tension"
        }

    top = tensions[:3]
    repetition_pull = round(sum(
        t.get("strength", 0) for t in top
        if t.get("winner") == "repetition"
    ), 3)
    variation_pull = round(sum(
        t.get("strength", 0) for t in top
        if t.get("winner") == "variation"
    ), 3)

    if repetition_pull >= 2 and repetition_pull > variation_pull:
        return {
            "bias": "repetition_momentum",
            "source": "tension_memory",
            "strength": repetition_pull,
            "opposing_strength": variation_pull
        }

    if variation_pull >= 2 and variation_pull > repetition_pull:
        return {
            "bias": "variation_momentum",
            "source": "tension_memory",
            "strength": variation_pull,
            "opposing_strength": repetition_pull
        }

    return {
        "bias": "tension_balance",
        "source": "tension_memory",
        "strength": max(repetition_pull, variation_pull),
        "opposing_strength": min(repetition_pull, variation_pull)
    }
