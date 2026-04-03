from fastapi import APIRouter, Body
from datetime import datetime, timezone
from pathlib import Path
import uuid, random, json, threading, time

router = APIRouter(prefix="/api/system", tags=["system"])

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "backend" / "data"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LEADERBOARD_FILE = DATA_DIR / "leaderboard.json"
FEEDBACK_FILE = DATA_DIR / "feedback.json"

RUNNING = False

def _now():
    return datetime.now(timezone.utc).isoformat()

def load_json(path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def score_candidate(title):
    score = random.uniform(6.0, 9.5)
    return round(score, 2)

def generate_concept():
    styles = ["fruit","animals","robots","fast food","objects"]
    formats = ["dating show","drama","chaos show","competition","sitcom"]
    style = random.choice(styles)
    fmt = random.choice(formats)

    title = f"{style.capitalize()} {fmt.title()}"
    hook = f"This {style} {fmt} just got out of control instantly."

    return {
        "id": uuid.uuid4().hex[:8],
        "title": title,
        "hook": hook,
        "created_at": _now()
    }

def evolve_cycle():
    leaderboard = load_json(LEADERBOARD_FILE, [])
    for _ in range(5):
        concept = generate_concept()
        concept["score"] = score_candidate(concept["title"])
        leaderboard.append(concept)

    leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:20]
    save_json(LEADERBOARD_FILE, leaderboard)

def background_loop():
    global RUNNING
    while RUNNING:
        evolve_cycle()
        time.sleep(10)

@router.post("/autopilot/start")
def start_autopilot():
    global RUNNING
    if RUNNING:
        return {"status":"already running"}

    RUNNING = True
    thread = threading.Thread(target=background_loop, daemon=True)
    thread.start()

    return {"status":"started","mode":"autonomous evolution"}

@router.post("/autopilot/stop")
def stop_autopilot():
    global RUNNING
    RUNNING = False
    return {"status":"stopped"}

@router.get("/leaderboard")
def get_leaderboard():
    return load_json(LEADERBOARD_FILE, [])

@router.post("/feedback")
def feedback(payload: dict = Body(...)):
    feedback_data = load_json(FEEDBACK_FILE, [])

    entry = {
        "id": payload.get("id"),
        "rating": payload.get("rating"),
        "timestamp": _now()
    }

    feedback_data.append(entry)
    save_json(FEEDBACK_FILE, feedback_data)

    return {"status":"saved"}
