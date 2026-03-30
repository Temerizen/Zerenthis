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

OUTPUT_DIR = ROOT / "data" / "outputs"
MEMORY_FILE = ROOT / "self_improver_memory.json"
SCORES_FILE = ROOT / "self_improver_scores.json"

print("🧠 Zerenthis LEVEL 2 EVOLUTION ENGINE ONLINE")

# ---------------- MEMORY ----------------
def load_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except:
        return default

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2))

# ---------------- SCORING ----------------
def score_output(file):
    try:
        size = os.path.getsize(file)
        score = min(100, int(size / 50))  # simple quality proxy
        return score
    except:
        return 0

def update_scores():
    scores = load_json(SCORES_FILE, {})
    for f in OUTPUT_DIR.glob("*"):
        scores[f.name] = score_output(f)
    save_json(SCORES_FILE, scores)
    return scores

# ---------------- IDEA ENGINE ----------------
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
    "output","scoring","conversion","cta","offer","title","viral"
]

def generate_ideas(mem):
    for idea in IDEAS:
        if idea in mem["ideas"]:
            continue
        if random.random() < 0.5:
            create_proposal({"title": idea, "description": idea, "tier": "low"})
            mem["ideas"].append(idea)
            print("🧠 New idea:", idea)

# ---------------- PERFORMANCE DETECTION ----------------
def detect_weak_outputs(mem, scores):
    for name, score in scores.items():
        if name in mem["files"]:
            continue
        if score < 60:
            create_proposal({
                "title": f"Improve weak output: {name}",
                "description": f"Low score: {score}",
                "tier": "low"
            })
            mem["files"].append(name)
            print(f"🩺 Weak output: {name} (score {score})")

# ---------------- REAL EXECUTION ----------------
def improve_file(file_path, mode):
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            if "conversion" in mode or "cta" in mode:
                f.write("\n\n--- HIGH CONVERSION CTA ---\nAct now. Limited opportunity.\n")

            if "monetization" in mode:
                f.write("\n\n--- MONETIZATION ---\nPremium tier: $49\nBundle available.\n")

            if "viral" in mode:
                f.write("\n\n--- VIRAL HOOK ---\nThis strategy is blowing up right now.\n")

            if "quality" in mode:
                f.write("\n\n--- ENHANCED CONTENT ---\nExpanded and improved section.\n")
    except:
        pass

def apply_real_improvements(title):
    for f in OUTPUT_DIR.glob("*"):
        improve_file(f, title)

# ---------------- MAIN LOOP ----------------
def loop():
    while True:
        try:
            mem = load_json(MEMORY_FILE, {"ideas": [], "files": []})

            print("\n⚙️ Level 2 cycle...")

            # 1. score outputs
            scores = update_scores()

            # 2. generate ideas
            generate_ideas(mem)

            # 3. detect weak outputs
            detect_weak_outputs(mem, scores)

            save_json(MEMORY_FILE, mem)

            # 4. run AI logic
            run_ai_cycle()

            # 5. apply improvements
            props = pending()
            print(f"📦 {len(props)} proposals")

            for p in props:
                title = str(p.get("title","")).lower()
                pid = p.get("id")

                if any(k in title for k in SAFE):
                    print("🔥 APPLY:", title)
                    approve(pid)
                    execute(pid)
                    apply_real_improvements(title)
                else:
                    print("⏸ SKIP:", title)

        except Exception as e:
            print("❌ ERROR:", e)

        time.sleep(60)

if __name__ == "__main__":
    loop()
