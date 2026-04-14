from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "backend" / "data"
LEADERBOARD_FILE = DATA_DIR / "leaderboard.json"
CURRENT_TOPIC_FILE = DATA_DIR / "current_topic.json"

def _read(path):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except:
        pass
    return {"leaders":[]}

def update_leaderboard(revenue, conversions):
    data = _read(LEADERBOARD_FILE)
    topic_data = json.loads(CURRENT_TOPIC_FILE.read_text())

    topic = topic_data["topic"]

    found = False
    for item in data["leaders"]:
        if item["topic"] == topic:
            item["revenue"] += revenue
            item["conversions"] += conversions
            found = True

    if not found:
        data["leaders"].append({
            "topic": topic,
            "revenue": revenue,
            "conversions": conversions
        })

    LEADERBOARD_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return {"status":"leaderboard_updated","topic":topic}

