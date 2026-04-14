from fastapi import APIRouter
from backend.app.engines.topic_engine import get_topics
import random

router = APIRouter()

@router.get("/api/targets")
def get_targets():
    topics = get_topics(5)

    results = []
    for t in topics:
        views = random.randint(500, 5000)
        clicks = random.randint(50, 500)
        conversions = random.randint(5, 50)
        revenue = conversions * random.randint(10, 50)

        ctr = clicks / views if views else 0
        cvr = conversions / clicks if clicks else 0

        score = revenue + (ctr * 100) + (cvr * 100)

        results.append({
            "topic": t,
            "revenue": revenue,
            "conversions": conversions,
            "views": views,
            "clicks": clicks,
            "ctr": ctr,
            "cvr": cvr,
            "total_score": score
        })

    results = sorted(results, key=lambda x: x["total_score"], reverse=True)

    return {
        "status": "multi_target_ranked",
        "top_targets": results,
        "current_topic_before": results[0]["topic"],
        "current_topic_after": results[0]["topic"],
        "switched": False
    }
