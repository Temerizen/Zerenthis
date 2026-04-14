import os, json

DATA_DIR = "backend/data"
OUT_DIR = "backend/outputs"

def exists(path):
    return os.path.exists(path)

def run():
    checks = {
        "current_topic": exists(os.path.join(DATA_DIR, "current_topic.json")),
        "leaderboard": exists(os.path.join(DATA_DIR, "leaderboard.json")),
        "performance_log": exists(os.path.join(DATA_DIR, "performance_log.json")),
        "posting_queue": exists(os.path.join(DATA_DIR, "posting_queue.json")),
        "posting_results": exists(os.path.join(DATA_DIR, "posting_results.json")),
        "ranked_targets": exists(os.path.join(DATA_DIR, "ranked_targets.json")),
        "phase_lock": exists(os.path.join(DATA_DIR, "phase_lock.json")),
        "campaign_outputs_present": exists(OUT_DIR)
    }

    passed = all(checks.values())

    return {
        "status": "phase_verified" if passed else "phase_verify_failed",
        "passed": passed,
        "checks": checks
    }
