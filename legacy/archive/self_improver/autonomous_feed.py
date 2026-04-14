import time
import sys
import random
import requests

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from self_improver.engine import create_proposal

print("🔥 Zerenthis FULL AUTONOMOUS MODE ONLINE")

API = "http://127.0.0.1:8000/api/product-pack"

TOPICS = [
    "make money online with AI",
    "AI automation side hustles",
    "passive income ideas 2026",
    "how to start digital products",
    "faceless YouTube automation",
    "AI business ideas that work",
    "online income for beginners",
    "high income skills with AI"
]

def generate_product():
    topic = random.choice(TOPICS)
    print("🚀 Generating:", topic)

    try:
        r = requests.post(API, json={"topic": topic}, timeout=30)
        print("📦 Created:", r.json())
    except Exception as e:
        print("❌ API error:", e)

def inject_evolution():
    ideas = [
        "Improve conversion of product packs",
        "Add monetization sections",
        "Improve CTA and sales copy",
        "Make outputs more viral"
    ]

    for idea in ideas:
        create_proposal({
            "title": idea,
            "description": idea,
            "tier": "low"
        })
        print("🧠 Injected:", idea)

def loop():
    while True:
        print("\n⚙️ FULL AUTONOMOUS CYCLE")

        # 1. create new product
        generate_product()

        # 2. inject improvements
        inject_evolution()

        # 3. wait before next cycle
        print("💤 Sleeping 90s...")
        time.sleep(90)

if __name__ == "__main__":
    loop()
