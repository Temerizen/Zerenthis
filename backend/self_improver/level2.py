import time
import sys
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from self_improver.worker import run_ai_cycle
from self_improver.engine import pending, approve, execute, create_proposal

OUTPUT_DIR = ROOT / "data" / "outputs"
MEMORY_FILE = ROOT / "self_improver_memory.json"

print("🧠 Zerenthis ACTIVE EVOLUTION ENGINE (NO-IDLE MODE)")

# -------- MEMORY --------
def load_mem():
    if not MEMORY_FILE.exists():
        return {"ideas": [], "last_forced": 0}
    try:
        return json.loads(MEMORY_FILE.read_text())
    except:
        return {"ideas": [], "last_forced": 0}

def save_mem(mem):
    MEMORY_FILE.write_text(json.dumps(mem, indent=2))

# -------- FORCE IDEAS --------
BASE_IDEAS = [
    "Improve conversion of product packs",
    "Increase output quality and depth",
    "Add stronger monetization sections",
    "Improve CTA and sales copy",
    "Make outputs more viral"
]

def force_generate(mem):
    new_count = 0

    for idea in BASE_IDEAS:
        if idea not in mem["ideas"]:
            create_proposal({
                "title": idea,
                "description": idea,
                "tier": "low"
            })
            mem["ideas"].append(idea)
            print("🧠 Injected:", idea)
            new_count += 1

    # 🔥 CRITICAL: if NOTHING new → force something anyway
    if new_count == 0:
        idea = random.choice(BASE_IDEAS)
        create_proposal({
            "title": idea + " (forced)",
            "description": idea,
            "tier": "low"
        })
        print("⚡ Forced idea:", idea)

# -------- WEAK OUTPUT TRIGGER --------
def detect_outputs():
    for f in OUTPUT_DIR.glob("*"):
        create_proposal({
            "title": f"Improve weak output: {f.name}",
            "description": "Auto-detected",
            "tier": "low"
        })
        print("🩺 Triggered improvement:", f.name)

# -------- APPLY ENGINE --------
SAFE = [
    "conversion","monetization","cta",
    "viral","quality","output","improve"
]

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

# -------- LOOP --------
def loop():
    while True:
        try:
            print("\n⚙️ NO-IDLE CYCLE")

            mem = load_mem()

            # 1. ALWAYS generate ideas
            force_generate(mem)

            # 2. ALWAYS trigger output improvements
            detect_outputs()

            save_mem(mem)

            # 3. run AI
            run_ai_cycle()

            # 4. apply everything valid
            apply()

        except Exception as e:
            print("❌ ERROR:", e)

        time.sleep(60)

if __name__ == "__main__":
    loop()
