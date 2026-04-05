import json
import os
from datetime import datetime, timezone

DATA_DIR = os.path.join("backend", "data")
LATEST_IDEA_PATH = os.path.join(DATA_DIR, "latest_builder_idea.json")

IDEAS = [
    {
        "title": "Faceless Content Cashflow Starter Pack",
        "niche": "Content Monetization",
        "buyer": "Beginners who want fast content and simple offers",
        "promise": "Launch useful content and a starter offer quickly",
        "offer": "$19 starter content bundle"
    },
    {
        "title": "Short-Form Growth Blueprint",
        "niche": "Creator Growth",
        "buyer": "Creators who want consistent short-form output",
        "promise": "Turn one idea into many posts fast",
        "offer": "$29 content system pack"
    },
    {
        "title": "No-Face Offer Engine",
        "niche": "Digital Products",
        "buyer": "Solo builders who want simple offers and faster publishing",
        "promise": "Build and publish monetizable assets without overcomplication",
        "offer": "$49 launch bundle"
    }
]

def _utc_now():
    return datetime.now(timezone.utc).isoformat()

def run_builder():
    os.makedirs(DATA_DIR, exist_ok=True)

    idx = datetime.now(timezone.utc).minute % len(IDEAS)
    base = IDEAS[idx]
    idea = {
        "created_at": _utc_now(),
        "title": base["title"],
        "niche": base["niche"],
        "buyer": base["buyer"],
        "promise": base["promise"],
        "offer": base["offer"],
        "angles": [
            "speed",
            "simplicity",
            "beginner-friendly monetization",
            "repurpose one idea into many assets"
        ]
    }

    with open(LATEST_IDEA_PATH, "w", encoding="utf-8") as f:
        json.dump(idea, f, indent=2)

    print(f"[BUILDER {idea['created_at']}] generated idea: {idea['title']}", flush=True)
    return idea
