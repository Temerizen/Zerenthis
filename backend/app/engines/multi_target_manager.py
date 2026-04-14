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

def build_candidates(leaderboard):
    candidates = []

    if not isinstance(leaderboard, dict):
        return candidates

    for topic, data in leaderboard.items():
        if topic == "leaders":
            continue
        if not isinstance(data, dict):
            continue

        revenue = float(data.get("revenue", 0) or 0)
        conversions = float(data.get("conversions", 0) or 0)
        views = float(data.get("views", 0) or 0)
        clicks = float(data.get("clicks", 0) or 0)
        reality_score = float(data.get("reality_score", 0) or 0)

        ctr = (clicks / views) if views > 0 else 0.0
        cvr = (conversions / clicks) if clicks > 0 else 0.0

        total_score = round(
            reality_score +
            (revenue * 0.25) +
            (conversions * 1.5) +
            (ctr * 100.0) +
            (cvr * 120.0),
            4
        )

        candidates.append({
            "topic": topic,
            "revenue": revenue,
            "conversions": conversions,
            "views": views,
            "clicks": clicks,
            "reality_score": reality_score,
            "ctr": round(ctr, 6),
            "cvr": round(cvr, 6),
            "total_score": total_score
        })

    candidates.sort(key=lambda x: x["total_score"], reverse=True)
    return candidates

def run(payload=None):
    payload = payload or {}
    limit = int(payload.get("limit", 5))

    leaderboard = safe_load(os.path.join(DATA_DIR, "leaderboard.json"), default={}) or {}
    current = safe_load(os.path.join(DATA_DIR, "current_topic.json"), default={}) or {}

    candidates = build_candidates(leaderboard)
    ranked = candidates[:limit]

    best = ranked[0] if ranked else {"topic": current.get("topic", "unknown_topic")}
    current_topic = current.get("topic", "unknown_topic")
    next_topic = best.get("topic", current_topic)

    switched = next_topic != current_topic

    safe_save(os.path.join(DATA_DIR, "ranked_targets.json"), ranked)
    safe_save(os.path.join(DATA_DIR, "current_topic.json"), {"topic": next_topic})

    return {
        "status": "multi_target_ranked",
        "current_topic_before": current_topic,
        "current_topic_after": next_topic,
        "switched": switched,
        "top_targets": ranked
    }

