import time
import sys
import os
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from self_improver.worker import run_ai_cycle
from self_improver.engine import pending, approve, execute, create_proposal

OUTPUT_DIR = ROOT / "data" / "outputs"

print("🧠 Zerenthis Autonomous Evolution ONLINE")

IDEAS = [
    "Improve conversion of product packs",
    "Increase output quality and depth",
    "Add stronger monetization sections",
    "Improve CTA and sales copy",
    "Make outputs more viral",
    "Enhance formatting and readability"
]

SAFE = [
    "quality","monetization","pricing","upsell","metadata",
    "output","scoring","conversion","cta","offer","title"
]

def generate_ideas():
    for idea in IDEAS:
        if random.random() < 0.6:
            create_proposal({"title": idea, "description": idea, "tier": "low"})
            print("🧠 Idea injected:", idea)

def detect_weak_outputs():
    if not OUTPUT_DIR.exists():
        return
    for f in OUTPUT_DIR.glob("*"):
        try:
            if os.path.getsize(f) < 3000:
                create_proposal({
                    "title": f"Improve weak output: {f.name}",
                    "description": "Low quality output detected",
                    "tier": "low"
                })
                print("🩺 Weak output:", f.name)
        except:
            pass

def loop():
    while True:
        try:
            print("\n⚙️ Evolution cycle...")
            generate_ideas()
            detect_weak_outputs()
            run_ai_cycle()

            props = pending()
            print(f"📦 {len(props)} proposals")

            for p in props:
                title = str(p.get("title","")).lower()
                pid = p.get("id")

                if any(k in title for k in SAFE):
                    print("🔥 APPLY:", title)
                    approve(pid)
                    execute(pid)
                else:
                    print("⏸ SKIP:", title)

        except Exception as e:
            print("❌ ERROR:", e)

        time.sleep(60)

if __name__ == "__main__":
    loop()
