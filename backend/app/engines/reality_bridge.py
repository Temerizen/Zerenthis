import os, json, time

DATA_DIR = "backend/data"

def safe_load(path, default=None):
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def safe_save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_active_target():
    ranked = safe_load(os.path.join(DATA_DIR, "ranked_targets.json"), default=[])
    if isinstance(ranked, list) and ranked:
        top = ranked[0]
        return {
            "topic": top.get("topic", "unknown_topic"),
            "source": "ranked_targets"
        }

    current = safe_load(os.path.join(DATA_DIR, "current_topic.json"), default={})
    return {
        "topic": current.get("topic", "unknown_topic"),
        "source": "current_topic"
    }

def compute_validation(signal):
    views = float(signal.get("views", 0) or 0)
    clicks = float(signal.get("clicks", 0) or 0)
    conversions = float(signal.get("conversions", 0) or 0)
    revenue = float(signal.get("revenue", 0) or 0)

    ctr = (clicks / views) if views > 0 else 0.0
    cvr = (conversions / clicks) if clicks > 0 else 0.0

    validation_score = round(
        (views * 0.005) +
        (clicks * 0.05) +
        (conversions * 1.5) +
        (revenue * 0.2),
        4
    )

    should_scale = conversions >= 3 and ctr >= 0.01 and cvr >= 0.01

    return {
        "ctr": round(ctr, 6),
        "cvr": round(cvr, 6),
        "validation_score": validation_score,
        "should_scale": should_scale
    }

def update_leaderboard(topic, validation, signal):
    leaderboard_path = os.path.join(DATA_DIR, "leaderboard.json")
    leaderboard = safe_load(leaderboard_path, default={}) or {}

    if topic not in leaderboard:
        leaderboard[topic] = {
            "revenue": 0,
            "conversions": 0,
            "views": 0,
            "clicks": 0,
            "reality_score": 0,
            "signals": []
        }

    entry = leaderboard[topic]
    entry["revenue"] = float(entry.get("revenue", 0)) + float(signal.get("revenue", 0) or 0)
    entry["conversions"] = float(entry.get("conversions", 0)) + float(signal.get("conversions", 0) or 0)
    entry["views"] = float(entry.get("views", 0)) + float(signal.get("views", 0) or 0)
    entry["clicks"] = float(entry.get("clicks", 0)) + float(signal.get("clicks", 0) or 0)
    entry["reality_score"] = round(float(entry.get("reality_score", 0)) + float(validation["validation_score"]), 4)

    compact_signal = {
        "timestamp": int(time.time()),
        "views": signal.get("views", 0),
        "clicks": signal.get("clicks", 0),
        "conversions": signal.get("conversions", 0),
        "revenue": signal.get("revenue", 0),
        "validation_score": validation["validation_score"],
        "should_scale": validation["should_scale"]
    }
    entry["signals"].append(compact_signal)

    safe_save(leaderboard_path, leaderboard)
    return leaderboard[topic]

def append_performance_log(topic, target_source, signal, validation):
    path = os.path.join(DATA_DIR, "performance_log.json")
    log = safe_load(path, default=[]) or []

    record = {
        "timestamp": int(time.time()),
        "topic": topic,
        "target_source": target_source,
        "views": signal.get("views", 0),
        "clicks": signal.get("clicks", 0),
        "conversions": signal.get("conversions", 0),
        "revenue": signal.get("revenue", 0),
        "ctr": validation["ctr"],
        "cvr": validation["cvr"],
        "validation_score": validation["validation_score"],
        "should_scale": validation["should_scale"],
        "safe_mode": True
    }

    log.append(record)
    safe_save(path, log)
    return record

def run(payload):
    active = get_active_target()
    topic = active["topic"]

    signal = {
        "views": payload.get("views", 0),
        "clicks": payload.get("clicks", 0),
        "conversions": payload.get("conversions", 0),
        "revenue": payload.get("revenue", 0)
    }

    validation = compute_validation(signal)
    performance_record = append_performance_log(topic, active["source"], signal, validation)
    updated_entry = update_leaderboard(topic, validation, signal)

    return {
        "status": "reality_signal_ingested",
        "topic": topic,
        "target_source": active["source"],
        "performance_record": performance_record,
        "leaderboard_entry": {
            "revenue": updated_entry.get("revenue", 0),
            "conversions": updated_entry.get("conversions", 0),
            "views": updated_entry.get("views", 0),
            "clicks": updated_entry.get("clicks", 0),
            "reality_score": updated_entry.get("reality_score", 0)
        },
        "decision_gate": {
            "should_scale": validation["should_scale"],
            "reason": "validation_passed" if validation["should_scale"] else "insufficient_validation"
        }
    }

