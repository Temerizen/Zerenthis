
def load_real_targets():
    out = []

    leaderboard = _read_json(LEADERBOARD_FILE, {})

    # ?? FORCE READ YOUR STRUCTURE
    if isinstance(leaderboard, dict):
        leaders = leaderboard.get("leaders", [])

        for item in leaders:
            topic = item.get("topic")
            if topic:
                out.append({
                    "topic": topic,
                    "niche": "validated",
                    "source": "leaderboard",
                    "revenue": float(item.get("revenue", 0)),
                    "conversions": float(item.get("conversions", 0))
                })

    return out


def score_target(t):
    source = t.get("source")

    revenue = t.get("revenue", 0)
    conversions = t.get("conversions", 0)

    # ?? REAL DOMINANCE SCORING
    real_score = (revenue * 2) + (conversions * 50)

    # ? SEEDS ARE NOW WEAK
    if source == "seed":
        real_score = random.uniform(10, 30)

    # ?? MASSIVE SOURCE BOOST
    source_bonus = {
        "locked": 200,
        "leaderboard": 150,
        "performance": 80,
        "seed": 0
    }.get(source, 0)

    total = real_score + source_bonus

    return {
        **t,
        "score_breakdown": {
            "revenue": revenue,
            "conversions": conversions,
            "base_score": round(real_score, 2),
            "source_bonus": source_bonus
        },
        "total_score": round(total, 2)
    }

