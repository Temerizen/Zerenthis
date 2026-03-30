import time
import sys
import os
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from self_improver.worker import run_ai_cycle
from self_improver.engine import pending, approve, execute, create_proposal, load

OUTPUT_DIR = ROOT / "data" / "outputs"
MEMORY_FILE = ROOT / "self_improver_memory.json"
COOLDOWN_FILE = ROOT / "self_improver_cooldowns.json"

print("🧠 Zerenthis DEDUPED LEVEL 2 ENGINE ONLINE")

def load_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except:
        return default

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2))

def normalize(text):
    return " ".join(str(text).lower().strip().split())

def current_titles():
    items = load()
    return [normalize(x.get("title", "")) for x in items]

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

COOLDOWN_SECONDS = 3600

def can_create(title, cooldowns):
    title_n = normalize(title)
    titles = current_titles()
    now = time.time()

    if title_n in titles:
        return False

    last = cooldowns.get(title_n, 0)
    if now - last < COOLDOWN_SECONDS:
        return False

    return True

def mark_created(title, cooldowns):
    cooldowns[normalize(title)] = time.time()

def generate_ideas(mem, cooldowns):
    for idea in IDEAS:
        if idea in mem["ideas"]:
            continue
        if random.random() < 0.5 and can_create(idea, cooldowns):
            create_proposal({
                "title": idea,
                "description": idea,
                "tier": "low"
            })
            mem["ideas"].append(idea)
            mark_created(idea, cooldowns)
            print("🧠 New idea:", idea)

def score_output(file):
    try:
        size = os.path.getsize(file)
        return min(100, int(size / 50))
    except:
        return 0

def detect_weak_outputs(mem, cooldowns):
    if not OUTPUT_DIR.exists():
        return

    for f in OUTPUT_DIR.glob("*"):
        score = score_output(f)
        title = f"Improve weak output: {f.name}"

        if f.name in mem["files"]:
            continue

        if score < 60 and can_create(title, cooldowns):
            create_proposal({
                "title": title,
                "description": f"Low score: {score}",
                "tier": "low"
            })
            mem["files"].append(f.name)
            mark_created(title, cooldowns)
            print(f"🩺 Weak output: {f.name} (score {score})")

def apply():
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

def loop():
    while True:
        try:
            mem = load_json(MEMORY_FILE, {"ideas": [], "files": []})
            cooldowns = load_json(COOLDOWN_FILE, {})

            print("\n⚙️ DEDUPED cycle...")

            generate_ideas(mem, cooldowns)
            detect_weak_outputs(mem, cooldowns)

            save_json(MEMORY_FILE, mem)
            save_json(COOLDOWN_FILE, cooldowns)

            run_ai_cycle()
            apply()

        except Exception as e:
            print("❌ ERROR:", e)

        time.sleep(120)

if __name__ == "__main__":
    loop()
