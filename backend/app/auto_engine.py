from fastapi import APIRouter, Body
from datetime import datetime, timezone
from pathlib import Path
import uuid, random, json, threading, time

router = APIRouter(prefix="/api/auto", tags=["auto"])

BASE = Path(__file__).resolve().parents[2]
DATA = BASE / "backend/data"
OUT = BASE / "backend/outputs"

DATA.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

LEADERBOARD = DATA / "auto_leaderboard.json"

RUN = False

def now():
    return datetime.now(timezone.utc).isoformat()

def load(p, d): return json.loads(p.read_text()) if p.exists() else d
def save(p, d): p.write_text(json.dumps(d, indent=2))

# -------- GENERATION --------
FORMATS = ["video","game","story","podcast"]
STYLES = ["fruit","robots","animals","chaos","absurd"]

def generate(prompt):
    fmt = random.choice(FORMATS)
    style = random.choice(STYLES)
    score = round(random.uniform(6, 10),2)

    return {
        "id": uuid.uuid4().hex[:8],
        "format": fmt,
        "style": style,
        "title": f"{style} {fmt}",
        "score": score,
        "created_at": now()
    }

# -------- EXPANSION --------
def expand(item):
    return {
        "video": f"{item['title']} short episode",
        "youtube": f"{item['title']} long form",
        "game": f"{item['title']} interactive concept",
        "comic": f"{item['title']} storyline",
        "podcast": f"{item['title']} discussion"
    }

# -------- CORE LOOP --------
def loop():
    global RUN
    while RUN:
        lb = load(LEADERBOARD, [])

        batch = [generate("auto") for _ in range(8)]
        best = sorted(batch, key=lambda x: x["score"], reverse=True)[0]

        expanded = expand(best)

        file = f"{uuid.uuid4().hex[:6]}.json"
        (OUT / file).write_text(json.dumps({
            "winner": best,
            "expansion": expanded
        }, indent=2))

        best["file"] = f"/api/file/{file}"
        lb.append(best)

        lb = sorted(lb, key=lambda x: x["score"], reverse=True)[:50]
        save(LEADERBOARD, lb)

        time.sleep(10)

# -------- ROUTES --------
@router.post("/start")
def start():
    global RUN
    if RUN:
        return {"status":"already running"}
    RUN = True
    threading.Thread(target=loop, daemon=True).start()
    return {"status":"started"}

@router.post("/stop")
def stop():
    global RUN
    RUN = False
    return {"status":"stopped"}

@router.get("/leaderboard")
def leaderboard():
    return load(LEADERBOARD, [])
