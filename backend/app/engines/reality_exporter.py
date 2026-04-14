import os, json, time

DATA_DIR = "backend/data"
OUT_DIR = "backend/outputs"

def safe_load(path, default=None):
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def run():
    topic_data = safe_load(os.path.join(DATA_DIR, "current_topic.json"), {})
    topic = topic_data.get("topic", "unknown_topic")

    campaign_file = os.path.join(OUT_DIR, f"campaign_{topic}.json")
    campaign = safe_load(campaign_file, {})

    perf_log = safe_load(os.path.join(DATA_DIR, "performance_log.json"), [])
    last_perf = perf_log[-1] if perf_log else {}

    export = {
        "topic": topic,
        "campaign": campaign,
        "last_performance": last_perf,
        "ready_for_real_world": True,
        "timestamp": int(time.time())
    }

    out_file = os.path.join(OUT_DIR, f"REAL_PACKAGE_{topic}.json")

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2)

    return {
        "status": "reality_package_ready",
        "file": out_file,
        "should_scale": last_perf.get("should_scale", False),
        "validation_score": last_perf.get("validation_score", 0)
    }

