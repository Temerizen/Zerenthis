import os, json, time
from backend.app.engines.reality_bridge import run as ingest_run

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

def run_result(payload):
    queue_path = os.path.join(DATA_DIR, "posting_queue.json")
    result_log_path = os.path.join(DATA_DIR, "posting_results.json")

    queue = safe_load(queue_path, default=[]) or []
    result_log = safe_load(result_log_path, default=[]) or []

    post_id = payload.get("id")
    if not post_id:
        return {"status": "missing_id"}

    match = None
    for item in queue:
        if item.get("id") == post_id:
            match = item
            break

    if not match:
        return {"status": "not_found", "id": post_id}

    result = {
        "timestamp": int(time.time()),
        "id": post_id,
        "topic": match.get("post", {}).get("topic"),
        "platform": match.get("post", {}).get("platform"),
        "views": payload.get("views", 0),
        "clicks": payload.get("clicks", 0),
        "conversions": payload.get("conversions", 0),
        "revenue": payload.get("revenue", 0)
    }

    result_log.append(result)
    safe_save(result_log_path, result_log)

    reality_response = ingest_run({
        "views": result["views"],
        "clicks": result["clicks"],
        "conversions": result["conversions"],
        "revenue": result["revenue"]
    })

    return {
        "status": "result_recorded",
        "result": result,
        "reality_ingestion": reality_response
    }
