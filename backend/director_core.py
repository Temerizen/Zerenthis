import json, random, os
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "backend" / "data"

DOCTRINE = DATA / "core" / "doctrine.json"
MEMORY = DATA / "autopilot" / "learning_log.json"
OUTPUT = DATA / "autopilot" / "director_plan.json"

def load(path, default):
    try:
        if path.exists():
            return json.load(open(path, "r", encoding="utf-8"))
    except:
        pass
    return default

def now():
    return datetime.utcnow().isoformat()

def build_plan():
    doctrine = load(DOCTRINE, {})
    memory = load(MEMORY, [])

    last = memory[-1] if memory else {}

    ideas = [
        "faceless tiktok monetization system",
        "ai product bundle for beginners",
        "high-conversion digital offer",
        "viral content engine"
    ]

    focus = random.choice(ideas)

    plan = {
        "time": now(),
        "focus": focus,
        "reason": "Selected based on system goals and memory",
        "next_steps": [
            f"build product around {focus}",
            "optimize for monetization",
            "generate distribution content"
        ],
        "doctrine": doctrine.get("rules", [])
    }

    return plan

def main():
    plan = build_plan()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(plan, open(OUTPUT, "w", encoding="utf-8"), indent=2)
    print("DIRECTOR PLAN CREATED:")
    print(json.dumps(plan, indent=2))

if __name__ == "__main__":
    main()
