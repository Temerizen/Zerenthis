import os, json, glob

DATA_DIR = "backend/data"
OUT_DIR = "backend/outputs"

def safe_load(path):
    try:
        if not path or not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def latest(pattern):
    files = glob.glob(pattern)
    return max(files, key=os.path.getctime) if files else None

def run():
    topic_data = safe_load(os.path.join(DATA_DIR, "current_topic.json")) or {}
    last_cycle = safe_load(os.path.join(DATA_DIR, "last_cycle.json")) or {}

    topic = topic_data.get("topic", "unknown_topic")

    hooks_file = latest(f"{OUT_DIR}/hooks_{topic}_*.json")
    posts_file = latest(f"{OUT_DIR}/posts_{topic}_*.json")
    scripts_file = latest(f"{OUT_DIR}/scripts_{topic}_*.json")

    hooks = safe_load(hooks_file) or []
    posts = safe_load(posts_file) or []
    scripts = safe_load(scripts_file) or []

    product = last_cycle.get("product") if last_cycle else {}

    campaign = {
        "topic": topic,
        "product": product or {},
        "traffic": {
            "hooks": hooks,
            "posts": posts,
            "scripts": scripts
        },
        "meta": {
            "hooks_count": len(hooks),
            "posts_count": len(posts),
            "scripts_count": len(scripts),
            "safe_mode": True
        }
    }

    out_file = f"{OUT_DIR}/campaign_{topic}.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(campaign, f, indent=2)

    return {
        "status": "campaign_built",
        "topic": topic,
        "file": out_file,
        "summary": campaign["meta"]
    }
