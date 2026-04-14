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

def run_execute(payload):
    queue_path = os.path.join(DATA_DIR, "posting_queue.json")
    publish_log_path = os.path.join(DATA_DIR, "publish_log.json")

    queue = safe_load(queue_path, default=[]) or []
    publish_log = safe_load(publish_log_path, default=[]) or []

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

    if match.get("status") == "published":
        return {"status": "already_published", "id": post_id}

    match["status"] = "published"
    match["published_at"] = int(time.time())

    publish_log.append({
        "timestamp": int(time.time()),
        "status": "post_published",
        "id": post_id,
        "topic": match.get("post", {}).get("topic"),
        "platform": match.get("post", {}).get("platform"),
        "simulate_only": match.get("simulate_only", True)
    })

    safe_save(queue_path, queue)
    safe_save(publish_log_path, publish_log)

    return {
        "status": "published",
        "id": post_id,
        "topic": match.get("post", {}).get("topic"),
        "platform": match.get("post", {}).get("platform")
    }
