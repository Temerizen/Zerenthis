import os
import json
from datetime import datetime

QUEUE_PATH = "backend/data/distribution_queue.json"

def _now():
    return datetime.utcnow().isoformat() + "Z"

def _load():
    if not os.path.exists(QUEUE_PATH):
        return []
    try:
        return json.load(open(QUEUE_PATH, "r", encoding="utf-8"))
    except:
        return []

def _save(data):
    json.dump(data, open(QUEUE_PATH, "w", encoding="utf-8"), indent=2)

def build_distribution_package(topic, buyer, promise, niche, script, variants):
    hashtags = [
        "#ai", "#makemoneyonline", "#contentcreator",
        "#tiktokgrowth", "#youtubeautomation"
    ]

    tiktok_posts = []
    for v in variants[:3]:
        tiktok_posts.append({
            "title": v["title"],
            "caption": f"{v['title']} for {buyer}. {promise}. " + " ".join(hashtags),
            "hook": v["hook"],
            "script": script[:200]
        })

    youtube_short = {
        "title": f"{topic} (Shorts)",
        "description": f"{topic} for {buyer}. {promise}",
        "tags": hashtags
    }

    youtube_long = {
        "title": f"{topic} FULL GUIDE",
        "description": f"{topic}\n\nFor {buyer}\nPromise: {promise}\nNiche: {niche}",
        "outline": [
            "Intro hook",
            "Core breakdown",
            "Steps",
            "Mistakes",
            "CTA"
        ]
    }

    return {
        "tiktok": tiktok_posts,
        "youtube_shorts": youtube_short,
        "youtube_long": youtube_long
    }

def enqueue(item):
    q = _load()
    item["id"] = len(q) + 1
    item["status"] = "pending"
    item["created_at"] = _now()
    q.insert(0, item)
    _save(q)
    return item

def get_queue(limit=10):
    return _load()[:limit]

def mark_posted(item_id):
    q = _load()
    for item in q:
        if item["id"] == item_id:
            item["status"] = "posted"
            item["posted_at"] = _now()
    _save(q)
    return {"status": "updated"}

