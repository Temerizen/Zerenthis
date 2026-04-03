import os
import json
from datetime import datetime

DATA_DIR = "backend/data"
PERFORMANCE_FILE = os.path.join(DATA_DIR, "performance.json")
LEARNING_FILE = os.path.join(DATA_DIR, "learning.json")

os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def log_performance(topic, platform="", views=0, likes=0, comments=0, shares=0, watch_time=0.0):
    rows = load_json(PERFORMANCE_FILE, [])
    row = {
        "topic": topic,
        "platform": platform,
        "views": int(views),
        "likes": int(likes),
        "comments": int(comments),
        "shares": int(shares),
        "watch_time": float(watch_time),
        "created_at": datetime.utcnow().isoformat()
    }
    rows.append(row)
    save_json(PERFORMANCE_FILE, rows)
    return row

def _keyword_bonus_map(rows):
    bonus = {}
    for row in rows:
        topic = (row.get("topic") or "").lower()
        views = int(row.get("views", 0))
        likes = int(row.get("likes", 0))
        comments = int(row.get("comments", 0))
        shares = int(row.get("shares", 0))
        watch_time = float(row.get("watch_time", 0.0))

        engagement = likes + (comments * 2) + (shares * 3)
        quality = 0

        if views >= 1000:
            quality += 2
        elif views >= 300:
            quality += 1

        if engagement >= 50:
            quality += 2
        elif engagement >= 10:
            quality += 1

        if watch_time >= 30:
            quality += 1

        words = [w.strip() for w in topic.replace("-", " ").split() if len(w.strip()) >= 3]
        for w in words:
            bonus[w] = bonus.get(w, 0) + quality

    return bonus

def rebuild_learning():
    rows = load_json(PERFORMANCE_FILE, [])
    topic_scores = {}
    keyword_scores = _keyword_bonus_map(rows)

    for row in rows:
        topic = row.get("topic") or ""
        views = int(row.get("views", 0))
        likes = int(row.get("likes", 0))
        comments = int(row.get("comments", 0))
        shares = int(row.get("shares", 0))
        watch_time = float(row.get("watch_time", 0.0))

        score = 0
        if views >= 1000:
            score += 3
        elif views >= 300:
            score += 2
        elif views >= 100:
            score += 1

        score += min(3, likes // 10)
        score += min(2, comments // 5)
        score += min(2, shares // 3)

        if watch_time >= 60:
            score += 2
        elif watch_time >= 20:
            score += 1

        topic_scores[topic] = topic_scores.get(topic, 0) + score

    learning = {
        "topic_scores": topic_scores,
        "keyword_scores": keyword_scores,
        "updated_at": datetime.utcnow().isoformat(),
        "samples": len(rows)
    }
    save_json(LEARNING_FILE, learning)
    return learning

def get_learning():
    return load_json(LEARNING_FILE, {"topic_scores": {}, "keyword_scores": {}, "updated_at": None, "samples": 0})

def get_learning_bonus(pack):
    learning = get_learning()
    topic_scores = learning.get("topic_scores", {})
    keyword_scores = learning.get("keyword_scores", {})

    topic = pack.get("topic") or ""
    topic_lower = topic.lower()

    bonus = 0

    if topic in topic_scores:
        bonus += min(5, int(topic_scores[topic]))

    words = [w.strip() for w in topic_lower.replace("-", " ").split() if len(w.strip()) >= 3]
    for w in words:
        bonus += min(2, int(keyword_scores.get(w, 0)))

    return min(8, bonus)
