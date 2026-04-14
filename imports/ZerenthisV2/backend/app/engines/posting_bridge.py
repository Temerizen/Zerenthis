import os, json, time, glob

DATA_DIR = "backend/data"
OUT_DIR = "backend/outputs"

def safe_load(path, default=None):
    try:
        if not path or not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def safe_save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def latest(pattern):
    files = glob.glob(pattern)
    return max(files, key=os.path.getctime) if files else None

def build_reddit_posts(topic, posts):
    built = []
    for i, body in enumerate(posts, start=1):
        title = f"{topic.replace('_',' ')[:90]} | practical breakdown #{i}"
        built.append({
            "platform": "reddit",
            "title": title,
            "body": body,
            "subreddit_hint": "sidehustle",
            "topic": topic
        })
    return built

def run(payload=None):
    payload = payload or {}
    simulate_only = payload.get("simulate_only", True)

    current = safe_load(os.path.join(DATA_DIR, "current_topic.json"), default={}) or {}
    topic = current.get("topic", "unknown_topic")

    campaign_file = os.path.join(OUT_DIR, f"campaign_{topic}.json")
    campaign = safe_load(campaign_file, default={}) or {}

    traffic = campaign.get("traffic", {})
    posts = traffic.get("posts", [])

    if not posts:
        posts_file = latest(f"{OUT_DIR}/posts_{topic}_*.json")
        posts = safe_load(posts_file, default=[]) or []

    reddit_posts = build_reddit_posts(topic, posts)

    queue_path = os.path.join(DATA_DIR, "posting_queue.json")
    queue = safe_load(queue_path, default=[]) or []

    ts = int(time.time())
    queued = []
    for item in reddit_posts:
        entry = {
            "id": f"{topic}_{ts}_{len(queued)+1}",
            "timestamp": ts,
            "simulate_only": simulate_only,
            "status": "queued_simulated" if simulate_only else "queued_live",
            "post": item
        }
        queue.append(entry)
        queued.append(entry)

    safe_save(queue_path, queue)

    publish_log_path = os.path.join(DATA_DIR, "publish_log.json")
    publish_log = safe_load(publish_log_path, default=[]) or []
    publish_log.append({
        "timestamp": ts,
        "topic": topic,
        "count": len(queued),
        "simulate_only": simulate_only,
        "status": "publish_simulated" if simulate_only else "publish_live_queued"
    })
    safe_save(publish_log_path, publish_log)

    out_file = os.path.join(OUT_DIR, f"posting_package_{topic}.json")
    safe_save(out_file, {
        "topic": topic,
        "simulate_only": simulate_only,
        "count": len(queued),
        "posts": queued
    })

    return {
        "status": "posting_bridge_ready",
        "topic": topic,
        "simulate_only": simulate_only,
        "queued": len(queued),
        "queue_file": queue_path,
        "package_file": out_file
    }
