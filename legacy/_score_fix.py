def score_target(t):
    source = t.get("source", "seed")

    # ?? REAL DATA TAKES OVER
    if source == "leaderboard":
        revenue = t.get("revenue", 0)
        conversions = t.get("conversions", 0)

        score = (revenue * 2) + (conversions * 50) + 100

        return {
            **t,
            "score_breakdown": {
                "revenue": revenue,
                "conversions": conversions,
                "mode": "REAL_DOMINANT"
            },
            "total_score": round(score, 2)
        }

    # ? SEEDS ARE NOW WEAK EXPLORATION ONLY
    score = random.uniform(10, 30)

    return {
        **t,
        "score_breakdown": {
            "mode": "exploration"
        },
        "total_score": round(score, 2)
    }
