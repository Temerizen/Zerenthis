from backend.app.engines.research_engine import run_research

def generate_targets():
    data = run_research()
    targets = []

    for item in data:
        score = (
            item["demand_score"] * 0.4 +
            item["monetization_score"] * 0.3 +
            item["trend_score"] * 0.2 -
            item["competition_score"] * 0.2
        )

        targets.append({
            "topic": item["topic"],
            "score": round(score, 2),
            "data": item
        })

    targets = sorted(targets, key=lambda x: x["score"], reverse=True)
    return targets
