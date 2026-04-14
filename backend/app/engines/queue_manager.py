import os, json, time
from backend.app.engines.posting_bridge import run as prepare_run

DATA_DIR = "backend/data"

# ---- config (safe defaults) ----
MAX_QUEUE = 10
LOW_WATERMARK = 3
COOLDOWN_SECONDS = 60
MIN_PRIORITY_TO_GENERATE = 0.0  # always allow, but influenced by score

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

def now():
    return int(time.time())

def count_active(queue):
    return len([q for q in (queue or []) if q.get("status") in ["queued_simulated","queued_live"]])

def last_publish_ts(publish_log):
    if not publish_log:
        return 0
    return max([e.get("timestamp",0) for e in publish_log])

def compute_priority(results, topic):
    # simple but effective: revenue + conversions weighted by recency
    if not results:
        return 0.0
    recent = [r for r in results if r.get("topic") == topic][-10:]
    if not recent:
        return 0.0

    score = 0.0
    for r in recent:
        rev = float(r.get("revenue",0))
        conv = float(r.get("conversions",0))
        views = float(r.get("views",0))
        clicks = float(r.get("clicks",0))
        ctr = (clicks / views) if views > 0 else 0.0
        cvr = (conv / clicks) if clicks > 0 else 0.0
        score += (rev * 0.5) + (conv * 2.0) + (ctr * 50.0) + (cvr * 100.0)

    return round(score, 3)

def run(payload=None):
    payload = payload or {}

    queue_path = os.path.join(DATA_DIR, "posting_queue.json")
    publish_log_path = os.path.join(DATA_DIR, "publish_log.json")
    results_path = os.path.join(DATA_DIR, "posting_results.json")
    current_topic_path = os.path.join(DATA_DIR, "current_topic.json")

    queue = safe_load(queue_path, default=[]) or []
    publish_log = safe_load(publish_log_path, default=[]) or []
    results = safe_load(results_path, default=[]) or []
    current = safe_load(current_topic_path, default={}) or {}

    topic = current.get("topic", "unknown_topic")

    active_q = count_active(queue)
    last_pub = last_publish_ts(publish_log)
    priority = compute_priority(results, topic)

    decision = {
        "topic": topic,
        "active_queue": active_q,
        "priority_score": priority,
        "cooldown_ok": (now() - last_pub) >= COOLDOWN_SECONDS,
        "under_max": active_q < MAX_QUEUE,
        "needs_refill": active_q < LOW_WATERMARK
    }

    # ---- decision logic ----
    if not decision["under_max"]:
        return {
            "status": "queue_full",
            "decision": decision,
            "action": "hold"
        }

    if not decision["cooldown_ok"]:
        return {
            "status": "cooldown_active",
            "decision": decision,
            "action": "hold"
        }

    # if low queue ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ always refill
    if decision["needs_refill"]:
        prep = prepare_run({"simulate_only": True})
        return {
            "status": "refilled_queue",
            "decision": decision,
            "action": "prepare",
            "prepare": prep
        }

    # otherwise, use priority to decide
    if priority >= MIN_PRIORITY_TO_GENERATE:
        prep = prepare_run({"simulate_only": True})
        return {
            "status": "priority_generate",
            "decision": decision,
            "action": "prepare",
            "prepare": prep
        }

    return {
        "status": "no_generate_low_priority",
        "decision": decision,
        "action": "hold"
    }

