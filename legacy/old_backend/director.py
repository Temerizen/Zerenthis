import os
import json
import random
from datetime import datetime

DATA_PATH = "backend/data/autopilot"

def load_winners():
    path = os.path.join(DATA_PATH, "winners.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_prompt():
    winners = load_winners()

    if not winners:
        return "Create a beginner-friendly digital product that makes money fast"

    best = winners[0]

    try:
        base = best["idea"]["prompt"]
    except Exception:
        base = "Improve a high-performing idea"

    upgrades = [
        "make it more viral",
        "increase emotional hooks",
        "focus on beginners",
        "make it easier to sell",
        "add urgency"
    ]

    return f"{base} and {random.choice(upgrades)}"

def save_prompt(prompt):
    os.makedirs(DATA_PATH, exist_ok=True)
    with open(os.path.join(DATA_PATH, "director_prompt.json"), "w", encoding="utf-8") as f:
        json.dump({
            "time": datetime.utcnow().isoformat(),
            "prompt": prompt
        }, f, indent=2)

def main():
    prompt = generate_prompt()
    save_prompt(prompt)
    print("Director updated strategy:", prompt)

if __name__ == "__main__":
    main()