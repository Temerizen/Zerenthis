def load_real_world_targets():
    out = []

    # 1. Load leaderboard (PRIMARY MONEY SIGNAL)
    leaderboard = _read_json(LEADERBOARD_FILE, {})
    if isinstance(leaderboard, dict):
        leaders = leaderboard.get("leaders", [])
        for item in leaders[:10]:
            if isinstance(item, dict):
                topic = item.get("topic")
                if topic:
                    out.append({
                        "topic": topic,
                        "niche": "validated",
                        "source": "leaderboard"
                    })

    # 2. Load performance log (secondary)
    perf = _read_json(PERF_FILE, [])
    if isinstance(perf, list):
        for item in perf[:10]:
            if isinstance(item, dict):
                topic = item.get("topic")
                if topic:
                    out.append({
                        "topic": topic,
                        "niche": "validated",
                        "source": "performance"
                    })

    return out
