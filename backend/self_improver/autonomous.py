import time
import sys
import os
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from self_improver.worker import run_ai_cycle
from self_improver.engine import pending, approve, execute, create_proposal

MEMORY_FILE = ROOT / "self_improver_memory.json"
OUTPUT_DIR = ROOT / "data" / "outputs"

def load_memory():
    if not MEMORY_FILE.exists():
        return {"ideas": [], "files": []}
    return json.loads(MEMORY_FILE.read_text())

def save_memory(mem):
    MEMORY_FILE.write_text(json.dumps(mem, indent=2))

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

def generate_ideas(mem):
    for idea in IDEAS:
        if idea in mem["ideas"]:
            continue
        if random.random() < 0.5:
            create_proposal({"title": idea, "description": idea, "tier": "low"})
            mem["ideas"].append(idea)
            print("🧠 New idea:", idea)

def detect_weak_outputs(mem):
    if not OUTPUT_DIR.exists():
        return
    for f in OUTPUT_DIR.glob("*"):
        fname = f.name
        if fname in mem["files"]:
            continue
        try:
            if os.path.getsize(f) < 3000:
                create_proposal({
                    "title": f"Improve weak output: {fname}",
                    "description": "Low quality output detected",
                    "tier": "low"
                })
                mem["files"].append(fname)
                print("🩺 Weak output (new):", fname)
        except:
            pass

def loop():
    print("🧠 Stable Evolution Engine ONLINE")

    while True:
        try:
            mem = load_memory()

            print("\n⚙️ Smart cycle...")
            generate_ideas(mem)
            detect_weak_outputs(mem)

            save_memory(mem)

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

        time.sleep(120)

if __name__ == "__main__":
    loop()
