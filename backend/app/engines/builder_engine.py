import os
import json
from datetime import datetime

DATA_DIR = os.path.join("backend", "data")
LATEST_IDEA_PATH = os.path.join(DATA_DIR, "latest_builder_idea.json")

def run_builder():
    os.makedirs(DATA_DIR, exist_ok=True)

    idea = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "title": "Faceless Content Cashflow Starter Pack",
        "niche": "Content Monetization",
        "buyer": "Beginners who want fast content and simple offers",
        "promise": "Launch useful content and a starter offer quickly",
        "offer": "$19 starter content bundle",
        "angles": [
            "speed",
            "simplicity",
            "beginner-friendly monetization",
            "repurposing one idea into many assets"
        ]
    }

    with open(LATEST_IDEA_PATH, "w", encoding="utf-8") as f:
        json.dump(idea, f, indent=2)

    print("Builder generated idea:", idea["title"])
    return idea
