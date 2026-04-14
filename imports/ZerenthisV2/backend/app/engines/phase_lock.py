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

def run():
    snapshot = {
        "timestamp": int(time.time()),
        "phase": "phase_3_controlled_autonomy_locked",
        "health_expected": True,
        "files": {
            "current_topic": os.path.join(DATA_DIR, "current_topic.json"),
            "leaderboard": os.path.join(DATA_DIR, "leaderboard.json"),
            "performance_log": os.path.join(DATA_DIR, "performance_log.json"),
            "posting_queue": os.path.join(DATA_DIR, "posting_queue.json"),
            "posting_results": os.path.join(DATA_DIR, "posting_results.json"),
            "ranked_targets": os.path.join(DATA_DIR, "ranked_targets.json"),
            "active_winner": os.path.join(DATA_DIR, "active_winner.json")
        }
    }

    out_path = os.path.join(DATA_DIR, "phase_lock.json")
    safe_save(out_path, snapshot)

    return {
        "status": "phase_locked",
        "file": out_path,
        "phase": snapshot["phase"]
    }
