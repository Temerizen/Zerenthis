import json, random
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "backend" / "data"

DOCTRINE = DATA / "core" / "doctrine.json"
OUTPUT = DATA / "autopilot" / "director_plan.json"

def load(path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return default

def now():
    return datetime.utcnow().isoformat()

def build_plan():
    doctrine = load(DOCTRINE, {})

    rules = doctrine.get("rules", [])
    goals = doctrine.get("goals", [])

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
        "reason": "Driven by doctrine goals",
        "next_steps": [
            f"build product around {focus}",
            "optimize for monetization",
            "generate distribution content"
        ],
        "rules": rules,
        "goals": goals
    }

    return plan

def main():
    plan = build_plan()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)

    print("DIRECTOR PLAN CREATED:")
    print(json.dumps(plan, indent=2))

if __name__ == "__main__":
    main()
