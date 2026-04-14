import os, json, glob

OUT_DIR = "backend/outputs"
DATA_DIR = "backend/data"

def latest(pattern):
    files = glob.glob(pattern)
    return max(files, key=os.path.getctime) if files else None

def load(path):
    try:
        if not path or not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def format_twitter(posts):
    return [f"{p}\n\n#AI #SideHustle #MakeMoney" for p in posts]

def format_reddit(posts):
    return [f"Title: {p[:60]}...\n\n{p}\n\nWhat do you think?" for p in posts]

def format_tiktok(scripts):
    return scripts

def run():
    topic_data = load(os.path.join(DATA_DIR, "current_topic.json")) or {}
    topic = topic_data.get("topic", "unknown")

    posts_file = latest(f"{OUT_DIR}/posts_{topic}_*.json")
    scripts_file = latest(f"{OUT_DIR}/scripts_{topic}_*.json")

    posts = load(posts_file) or []
    scripts = load(scripts_file) or []

    twitter = format_twitter(posts)
    reddit = format_reddit(posts)
    tiktok = format_tiktok(scripts)

    out = {
        "topic": topic,
        "twitter": twitter,
        "reddit": reddit,
        "tiktok": tiktok
    }

    out_file = f"{OUT_DIR}/REAL_TRAFFIC_{topic}.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    return {
        "status": "real_traffic_ready",
        "file": out_file,
        "counts": {
            "twitter": len(twitter),
            "reddit": len(reddit),
            "tiktok": len(tiktok)
        }
    }
