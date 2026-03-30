import time
import sys
import os
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from self_improver.worker import run_ai_cycle
from self_improver.engine import pending, approve, execute, create_proposal, load

OUTPUT_DIR = ROOT / "data" / "outputs"
MEMORY_FILE = ROOT / "self_improver_memory.json"
SCORES_FILE = ROOT / "self_improver_scores.json"
COOLDOWN_FILE = ROOT / "self_improver_cooldowns.json"

print("🧠 Zerenthis PERFORMANCE EVOLUTION ENGINE ONLINE")

SAFE = [
    "quality","monetization","pricing","upsell","metadata",
    "output","scoring","conversion","cta","offer","title","viral",
    "retention","structure","depth"
]

COOLDOWN_SECONDS = 300

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

def can_create(title, cooldowns):
    now = time.time()
    title_n = normalize(title)

    if title_n in current_titles():
        return False

    last = cooldowns.get(title_n, 0)
    return now - last >= COOLDOWN_SECONDS

def mark_created(title, cooldowns):
    cooldowns[normalize(title)] = time.time()

def score_output(file_path):
    try:
        size = os.path.getsize(file_path)
        text_bonus = 0

        # crude scoring proxy from file size
        if size >= 12000:
            text_bonus += 25
        elif size >= 8000:
            text_bonus += 18
        elif size >= 5000:
            text_bonus += 10
        elif size >= 3000:
            text_bonus += 5

        # reward recent updates a little
        age_seconds = max(1, time.time() - os.path.getmtime(file_path))
        freshness_bonus = 10 if age_seconds < 600 else 0

        score = min(100, int((size / 200) + text_bonus + freshness_bonus))
        return score
    except:
        return 0

def update_scores():
    scores = load_json(SCORES_FILE, {})

    for f in OUTPUT_DIR.glob("*"):
        if not f.is_file():
            continue

        current = score_output(f)
        previous = scores.get(f.name, {}).get("current_score", 0)

        scores[f.name] = {
            "current_score": current,
            "previous_score": previous,
            "delta": current - previous,
            "updated_at": time.time(),
        }

    save_json(SCORES_FILE, scores)
    return scores

def performance_based_proposals(scores, cooldowns, memory):
    if not scores:
        return

    ranked = sorted(
        scores.items(),
        key=lambda kv: (kv[1].get("current_score", 0), kv[1].get("delta", 0))
    )

    for name, info in ranked[:3]:
        current = info.get("current_score", 0)
        delta = info.get("delta", 0)

        # weak output
        if current < 60:
            title = f"Improve weak output: {name}"
            if can_create(title, cooldowns):
                create_proposal({
                    "title": title,
                    "description": f"Performance score is weak ({current})",
                    "tier": "low"
                })
                mark_created(title, cooldowns)
                print(f"🩺 Weak output proposal: {name} ({current})")

            title = f"Add stronger monetization sections to {name}"
            if can_create(title, cooldowns):
                create_proposal({
                    "title": title,
                    "description": f"Low-scoring output needs monetization upgrade ({current})",
                    "tier": "low"
                })
                mark_created(title, cooldowns)
                print(f"💸 Monetization proposal: {name}")

        # stagnating output
        if current < 80 and delta <= 0:
            title = f"Improve CTA and sales copy for {name}"
            if can_create(title, cooldowns):
                create_proposal({
                    "title": title,
                    "description": f"Output score is stagnating (score {current}, delta {delta})",
                    "tier": "low"
                })
                mark_created(title, cooldowns)
                print(f"📣 CTA proposal: {name}")

            title = f"Increase output quality and depth for {name}"
            if can_create(title, cooldowns):
                create_proposal({
                    "title": title,
                    "description": f"Output is not improving enough (score {current}, delta {delta})",
                    "tier": "low"
                })
                mark_created(title, cooldowns)
                print(f"📈 Depth proposal: {name}")

        # decent but not strong enough
        if 60 <= current < 85 and delta <= 2:
            title = f"Improve conversion of product pack: {name}"
            if can_create(title, cooldowns):
                create_proposal({
                    "title": title,
                    "description": f"Medium-performing output needs conversion lift (score {current})",
                    "tier": "low"
                })
                mark_created(title, cooldowns)
                print(f"🎯 Conversion proposal: {name}")

def apply():
    props = pending()
    print(f"📦 {len(props)} proposals")

    for p in props:
        title = str(p.get("title","")).lower()
        pid = p.get("id")

        if any(k in title for k in SAFE):
            print("🔥 APPLY:", title)
            approve(pid)
            result = execute(pid)
            print("⚙️ RESULT:", result)
        else:
            print("⏸ SKIP:", title)

def loop():
    while True:
        try:
            print("\n⚙️ PERFORMANCE cycle...")

            memory = load_json(MEMORY_FILE, {"ideas": [], "files": []})
            cooldowns = load_json(COOLDOWN_FILE, {})

            scores = update_scores()
            performance_based_proposals(scores, cooldowns, memory)

            save_json(MEMORY_FILE, memory)
            save_json(COOLDOWN_FILE, cooldowns)

            run_ai_cycle()
            apply()

        except Exception as e:
            print("❌ ERROR:", e)

        time.sleep(120)

if __name__ == "__main__":
    loop()
