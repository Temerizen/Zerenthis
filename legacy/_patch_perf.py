def load_performance_targets():
    data = _read_json(PERF_FILE, [])
    out = []

    # CASE 1: list (already works)
    if isinstance(data, list):
        for item in data[:10]:
            if isinstance(item, dict):
                topic = item.get("topic") or item.get("title") or item.get("name")
                if topic:
                    out.append({
                        "topic": topic,
                        "niche": item.get("niche", "performance"),
                        "source": "performance"
                    })

    # CASE 2: dict with leaders (YOUR CASE)
    elif isinstance(data, dict):
        entries = data.get("leaders") or data.get("entries") or data.get("history") or []

        for item in entries[:10]:
            if isinstance(item, dict):
                topic = item.get("topic") or item.get("title") or item.get("name")
                if topic:
                    out.append({
                        "topic": topic,
                        "niche": item.get("niche", "performance"),
                        "source": "performance"
                    })

    return out
