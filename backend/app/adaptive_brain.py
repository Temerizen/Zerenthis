from fastapi import APIRouter, Body
from pathlib import Path
from datetime import datetime, timezone
import json, random, threading, time

router = APIRouter(prefix="/api/brain", tags=["brain"])

BASE = Path(__file__).resolve().parents[2]
DATA = BASE / "backend" / "data"
DATA.mkdir(parents=True, exist_ok=True)

STATE_FILE = DATA / "brain_state.json"

RUNNING = False
THREAD = None

STYLES = ["fruit", "animals", "robots", "fast food", "objects"]
FORMATS = ["viral short", "youtube episode", "animated skit", "podcast bit", "comic arc", "game loop"]
HOOKS = [
    "Nobody expected this to happen",
    "This got out of control instantly",
    "This is the funniest thing online right now",
    "This might be the messiest episode yet",
    "You will not believe what happens next"
]
TWISTS = ["betrayal", "shock reveal", "public embarrassment", "secret alliance", "elimination"]

def now():
    return datetime.now(timezone.utc).isoformat()

def default_state():
    return {
        "updated_at": now(),
        "cycles": 0,
        "status": "idle",
        "weights": {
            "styles": {k: 1.0 for k in STYLES},
            "formats": {k: 1.0 for k in FORMATS},
            "hooks": {k: 1.0 for k in HOOKS},
            "twists": {k: 1.0 for k in TWISTS}
        },
        "top_patterns": [],
        "history": []
    }

def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default_state()

def save_state(state):
    state["updated_at"] = now()
    state["history"] = state.get("history", [])[-60:]
    state["top_patterns"] = state.get("top_patterns", [])[:20]
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")

def weighted_choice(items, weight_map):
    weights = [max(0.1, float(weight_map.get(x, 1.0))) for x in items]
    return random.choices(items, weights=weights, k=1)[0]

def simulate_quality(style, fmt, hook, twist):
    score = 6.4
    if style in ["fruit", "fast food", "objects"]:
        score += 0.5
    if fmt in ["viral short", "animated skit", "youtube episode"]:
        score += 0.4
    if "out of control" in hook.lower() or "funniest" in hook.lower():
        score += 0.5
    if twist in ["betrayal", "shock reveal", "elimination"]:
        score += 0.5
    score += random.uniform(-0.35, 0.55)
    return round(max(1.0, min(10.0, score)), 2)

def adapt_once():
    state = load_state()
    w = state["weights"]

    style = weighted_choice(STYLES, w["styles"])
    fmt = weighted_choice(FORMATS, w["formats"])
    hook = weighted_choice(HOOKS, w["hooks"])
    twist = weighted_choice(TWISTS, w["twists"])

    quality = simulate_quality(style, fmt, hook, twist)

    bump = 0.12 if quality >= 7.8 else (-0.06 if quality < 7.0 else 0.03)

    w["styles"][style] = round(max(0.2, min(5.0, w["styles"].get(style, 1.0) + bump)), 3)
    w["formats"][fmt] = round(max(0.2, min(5.0, w["formats"].get(fmt, 1.0) + bump)), 3)
    w["hooks"][hook] = round(max(0.2, min(5.0, w["hooks"].get(hook, 1.0) + bump)), 3)
    w["twists"][twist] = round(max(0.2, min(5.0, w["twists"].get(twist, 1.0) + bump)), 3)

    state["cycles"] = int(state.get("cycles", 0)) + 1
    state["status"] = "running"

    pattern = {
        "time": now(),
        "style": style,
        "format": fmt,
        "hook": hook,
        "twist": twist,
        "quality": quality
    }
    state.setdefault("history", []).append(pattern)

    ranked = sorted(state["history"], key=lambda x: x.get("quality", 0), reverse=True)
    state["top_patterns"] = ranked[:20]

    save_state(state)

def loop(interval_sec):
    global RUNNING
    while RUNNING:
        try:
            adapt_once()
        except Exception:
            pass
        time.sleep(interval_sec)

@router.post("/start")
def start(payload: dict = Body(default={})):
    global RUNNING, THREAD
    if RUNNING:
        return {"status": "already_running", "state": load_state()}
    interval_sec = int(payload.get("interval_sec", 45))
    RUNNING = True
    THREAD = threading.Thread(target=loop, args=(interval_sec,), daemon=True)
    THREAD.start()
    state = load_state()
    state["status"] = "running"
    save_state(state)
    return {"status": "started", "interval_sec": interval_sec, "state": state}

@router.post("/stop")
def stop():
    global RUNNING
    RUNNING = False
    state = load_state()
    state["status"] = "stopped"
    save_state(state)
    return {"status": "stopped", "state": state}

@router.get("/status")
def status():
    state = load_state()
    state["running"] = RUNNING
    return state

@router.post("/reset")
def reset():
    state = default_state()
    save_state(state)
    return {"status": "reset", "state": state}
