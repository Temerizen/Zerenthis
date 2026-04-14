import random
from datetime import datetime

def run_research():
    # REAL structured research simulation (replace later with APIs)
    base_topics = [
        "ai side hustle automation",
        "faceless content systems",
        "productivity systems for overwhelmed people",
        "make money with no money systems",
        "dopamine reset productivity",
        "ai business kits",
        "freelancing with ai automation"
    ]

    enriched = []
    for topic in base_topics:
        enriched.append({
            "topic": topic,
            "demand_score": round(random.uniform(6, 10), 2),
            "competition_score": round(random.uniform(3, 9), 2),
            "monetization_score": round(random.uniform(6, 10), 2),
            "trend_score": round(random.uniform(6, 10), 2),
            "timestamp": datetime.utcnow().isoformat()
        })

    return enriched

