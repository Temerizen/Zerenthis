import json
from pathlib import Path
from datetime import datetime
import random

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "backend" / "data"
OUTPUT_FILE = DATA_DIR / "ranked_targets.json"
LEADERBOARD_FILE = DATA_DIR / "leaderboard.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)

def _read_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default

def generate_seed_targets():
    return [
        {"topic": "ai side hustle system", "source": "seed"},
        {"topic": "dopamine reset system", "source": "seed"},
        {"topic": "faceless content automation", "source": "seed"}
    ]

def load_real_targets():
    data = _read_json(LEADERBOARD_FILE, {})
    out = []

    if isinstance(data, dict):
        for item in data.get("leaders", []):
            topic = item.get("topic")
            if topic:
                out.append({
                    "topic": topic,
                    "source": "leaderboard",
                    "revenue": item.get("revenue", 0),
                    "conversions": item.get("conversions", 0)
                })

    return out

def score_target(t):
    if t.get("source") == "leaderboard":
        score = (t.get("revenue", 0) * 2) + (t.get("conversions", 0) * 50) + 100
        return {**t, "total_score": score}

    return {**t, "total_score": round(random.uniform(10, 30), 4)}

def run_priority_engine():
    real = load_real_targets()
    seeds = generate_seed_targets()
    targets = real + seeds

    ranked = sorted(
        [score_target(t) for t in targets],
        key=lambda x: x["total_score"],
        reverse=True
    )

    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "candidate_count": len(targets),
        "top_target": ranked[0] if ranked else None,
        "ranked": ranked
    }

    OUTPUT_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result

