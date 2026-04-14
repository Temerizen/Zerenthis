import os, json, time

from backend.app.engines.traffic_factory import run as traffic_run

DATA_DIR = "backend/data"

def safe_load(path, default=None):
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def run():
    perf_log = safe_load(os.path.join(DATA_DIR, "performance_log.json"), default=[])
    last = perf_log[-1] if perf_log else None

    if not last:
        return {"status": "no_data"}

    should_scale = last.get("should_scale", False)
    topic = last.get("topic", "unknown")

    if not should_scale:
        return {
            "status": "no_scale",
            "topic": topic
        }

    # SCALE ACTION: generate more traffic
    outputs = []
    for _ in range(3):
        outputs.append(traffic_run())

    # mark winner
    winner_path = os.path.join(DATA_DIR, "active_winner.json")
    with open(winner_path, "w", encoding="utf-8") as f:
        json.dump({
            "topic": topic,
            "timestamp": int(time.time()),
            "scaled": True
        }, f, indent=2)

    return {
        "status": "scaled",
        "topic": topic,
        "bursts": len(outputs)
    }
