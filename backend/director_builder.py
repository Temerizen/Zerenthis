import os
import json
import random
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "backend" / "data" / "autopilot"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DIRECTOR_FILE = DATA_DIR / "director_prompt.json"
WINNERS_FILE = DATA_DIR / "winners.json"
MEMORY_FILE = DATA_DIR / "director_memory.json"

EMPIRE_VISIONS = [
    "build the best AI system in the world",
    "create automated money machines",
    "generate digital products that sell",
    "build faceless content empires",
    "improve intelligence, research, and execution",
    "create systems that learn from winners and scale what works",
    "turn Zerenthis into a founder-controlled command center",
    "prioritize outputs that create money, traction, and proof"
]

DEFAULT_IDEAS = [
    {
        "title": "Empire Cash Engine",
        "prompt": "Build a high-converting workflow that creates a premium digital product for beginners and distributes it through faceless short-form content."
    },
    {
        "title": "AI Product Factory",
        "prompt": "Build a workflow that generates an AI guide, offer, hooks, and distribution assets for creators who want faster monetization."
    },
    {
        "title": "Faceless Content Money System",
        "prompt": "Build a workflow for creating and selling a faceless content monetization package with strong hooks and clear calls to action."
    }
]

def now():
    return datetime.now(timezone.utc).isoformat()

def read_json(path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_winners():
    data = read_json(WINNERS_FILE, [])
    return data if isinstance(data, list) else []

def get_memory():
    data = read_json(MEMORY_FILE, {"history": []})
    if not isinstance(data, dict):
        data = {"history": []}
    data.setdefault("history", [])
    return data

def save_memory(entry):
    mem = get_memory()
    mem["history"].append(entry)
    mem["history"] = mem["history"][-100:]
    write_json(MEMORY_FILE, mem)

def choose_strategy():
    winners = get_winners()

    if winners:
        best = winners[0]
        try:
            base_prompt = best["idea"]["prompt"]
        except Exception:
            base_prompt = "Improve the highest-performing monetization workflow."
        style = random.choice([
            "make it more specific",
            "make it more beginner-friendly",
            "increase emotional hooks",
            "make the offer easier to buy",
            "focus on faster monetization",
            "improve proof and clarity"
        ])
        title = "Director Upgraded Winner"
        prompt = f"{base_prompt} Also {style}. Align it with these empire goals: " + "; ".join(EMPIRE_VISIONS[:4])
        source = "winner_memory"
    else:
        chosen = random.choice(DEFAULT_IDEAS)
        title = chosen["title"]
        prompt = chosen["prompt"] + " Align it with these empire goals: " + "; ".join(EMPIRE_VISIONS[:4])
        source = "default_vision"

    strategy = {
        "time": now(),
        "title": title,
        "prompt": prompt,
        "source": source,
        "visions": EMPIRE_VISIONS
    }
    return strategy

def main():
    strategy = choose_strategy()
    write_json(DIRECTOR_FILE, strategy)
    save_memory({
        "time": strategy["time"],
        "title": strategy["title"],
        "source": strategy["source"],
        "prompt": strategy["prompt"]
    })
    print("Director Builder strategy written:")
    print(json.dumps(strategy, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()