def load_leaderboard_targets():
    data = _read_json(LEADERBOARD_FILE, {})
    out = []

    items = []

    if isinstance(data, dict):
        items = data.get("leaders") or data.get("entries") or data.get("data") or []
    elif isinstance(data, list):
        items = data

    for item in items:
        if isinstance(item, dict):
            topic = item.get("topic") or item.get("title") or item.get("name")
            if topic:
                out.append({
                    "topic": topic,
                    "niche": "validated",
                    "source": "leaderboard",
                    "revenue": float(item.get("revenue", 0)),
                    "conversions": float(item.get("conversions", 0))
                })

    return out
