import os
import json
from datetime import datetime

DATA_DIR = os.path.join("backend", "data")
OUTPUT_DIR = os.path.join("backend", "outputs")
LATEST_IDEA_PATH = os.path.join(DATA_DIR, "latest_builder_idea.json")

def run_money():
    print("💰 Money engine running...")
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if os.path.exists(LATEST_IDEA_PATH):
        with open(LATEST_IDEA_PATH, "r", encoding="utf-8") as f:
            idea = json.load(f)
    else:
        idea = {
            "title": "Starter Offer",
            "niche": "General",
            "buyer": "General audience",
            "promise": "Get started quickly",
            "offer": "$19 starter bundle"
        }

    filename = f"money_offer_{int(datetime.now().timestamp())}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("Zerenthis Money Output\n")
        f.write(f"Title: {idea.get('title', 'Starter Offer')}\n")
        f.write(f"Niche: {idea.get('niche', 'General')}\n")
        f.write(f"Buyer: {idea.get('buyer', 'General audience')}\n")
        f.write(f"Promise: {idea.get('promise', 'Useful result')}\n")
        f.write(f"Offer: {idea.get('offer', '$19 starter bundle')}\n")

    print("💸 Product generated:", filepath)
