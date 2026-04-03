from fastapi import APIRouter, Body
from datetime import datetime, timezone
from pathlib import Path
import uuid, random, json, threading, time

router = APIRouter(prefix="/api/system", tags=["system"])

BASE = Path(__file__).resolve().parents[2]
DATA = BASE / "backend/data"
OUT = BASE / "backend/outputs"

DATA.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

STATE_FILE = DATA / "autopilot_state.json"
QUEUE_FILE = DATA / "queue.json"
LEADERBOARD_FILE = DATA / "leaderboard.json"
FEEDBACK_FILE = DATA / "feedback.json"

# --------- utils ---------
def now():
    return datetime.now(timezone.utc).isoformat()

def load(p, d):
    return json.loads(p.read_text()) if p.exists() else d

def save(p, d):
    p.write_text(json.dumps(d, indent=2), encoding="utf-8")

def slug(s):
    return "".join(c.lower() if c.isalnum() else "_" for c in s)[:60]

# --------- simple trend + taste ---------
STYLES = ["fruit","animals","robots","fast food","objects"]
FORMATS = ["dating show","elimination show","chaos reality show","sitcom","competition"]
TWISTS = ["betrayal","shock elimination","secret alliance","public humiliation"]
HOOKS = [
    "Nobody was ready for this",
    "This got out of control instantly",
    "You won't believe what happens next",
    "This might be the funniest episode yet"
]

def bias_from_feedback():
    fb = load(FEEDBACK_FILE, [])
    if not fb: 
        return {}
    styles = {}
    formats = {}
    for x in fb:
        if x.get("rating",0) >= 4:
            s = x.get("style"); f = x.get("format")
            if s: styles[s] = styles.get(s,0)+1
            if f: formats[f] = formats.get(f,0)+1
    return {"styles": styles, "formats": formats}

def weighted_choice(options, weights_map):
    if not weights_map:
        return random.choice(options)
    weights = []
    for o in options:
        weights.append(1 + weights_map.get(o,0))
    return random.choices(options, weights=weights, k=1)[0]

def generate_candidate(prompt):
    bias = bias_from_feedback()
    style = weighted_choice(STYLES, bias.get("styles", {}))
    fmt = weighted_choice(FORMATS, bias.get("formats", {}))
    twist = random.choice(TWISTS)
    hook = random.choice(HOOKS)

    score = round(min(random.uniform(6.5, 9.8) + (0.4 if style in ["fruit","fast food","objects"] else 0), 10), 2)

    return {
        "id": uuid.uuid4().hex[:8],
        "prompt": prompt,
        "title": f"{style.capitalize()} {fmt}",
        "style": style,
        "format": fmt,
        "hook": hook,
        "twist": twist,
        "score": score,
        "created_at": now()
    }

def taste_gate(items, min_score=7.8):
    return [x for x in items if x["score"] >= min_score]

def evolve(prompt, rounds=3, batch=6):
    pop = [generate_candidate(prompt) for _ in range(batch)]
    for _ in range(rounds):
        pop = sorted(pop, key=lambda x: x["score"], reverse=True)[:2]
        while len(pop) < batch:
            pop.append(generate_candidate(prompt))
    return sorted(pop, key=lambda x: x["score"], reverse=True)

# --------- media pack (lightweight) ---------
def build_pack(w):
    return {
        "tiktok": {
            "hook": w["hook"],
            "caption": f"{w['title']} is already chaos. Follow for episode 2."
        },
        "youtube": {
            "title": f"{w['title']} | Episode 1",
            "idea": f"Longer episode built around {w['twist']}"
        },
        "podcast": {
            "topic": f"Inside the drama of {w['title']}"
        },
        "comic": {
            "arc": f"A 5-part arc centered on {w['twist']}"
        },
        "game": {
            "concept": f"Interactive {w['format']} with eliminations and alliances"
        }
    }

# --------- core loop ---------
RUN = False
THREAD = None

def loop():
    global RUN
    while RUN:
        state = load(STATE_FILE, {"interval_sec": 20, "prompt": "viral chaos series", "rounds": 3, "batch": 6})
        prompt = state.get("prompt","viral chaos series")
        rounds = int(state.get("rounds",3))
        batch = int(state.get("batch",6))

        ranked = evolve(prompt, rounds=rounds, batch=batch)
        ranked = taste_gate(ranked) or ranked[:2]

        queue = load(QUEUE_FILE, [])
        leaderboard = load(LEADERBOARD_FILE, [])

        for w in ranked[:2]:
            pack = build_pack(w)
            file = f"{slug(prompt)}_{uuid.uuid4().hex[:6]}.json"
            (OUT / file).write_text(json.dumps({"winner": w, "media": pack}, indent=2), encoding="utf-8")

            item = {
                "id": w["id"],
                "title": w["title"],
                "style": w["style"],
                "format": w["format"],
                "score": w["score"],
                "file": f"/api/file/{file}",
                "created_at": now()
            }
            queue.append(item)
            leaderboard.append(item)

        leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:50]

        save(QUEUE_FILE, queue)
        save(LEADERBOARD_FILE, leaderboard)

        time.sleep(int(state.get("interval_sec", 20)))

# --------- routes ---------
@router.post("/autopilot/start")
def start(payload: dict = Body(default={})):
    global RUN, THREAD
    if RUN:
        return {"status":"already_running"}

    state = {
        "interval_sec": int(payload.get("interval_sec", 20)),
        "prompt": payload.get("prompt", "viral chaos series"),
        "rounds": int(payload.get("rounds", 3)),
        "batch": int(payload.get("batch", 6))
    }
    save(STATE_FILE, state)

    RUN = True
    THREAD = threading.Thread(target=loop, daemon=True)
    THREAD.start()

    return {"status":"started","state":state}

@router.post("/autopilot/stop")
def stop():
    global RUN
    RUN = False
    return {"status":"stopped"}

@router.get("/queue")
def get_queue():
    return load(QUEUE_FILE, [])

@router.get("/leaderboard")
def get_leaderboard():
    return load(LEADERBOARD_FILE, [])

@router.post("/approve")
def approve(payload: dict = Body(...)):
    fb = load(FEEDBACK_FILE, [])
    entry = {
        "id": payload.get("id"),
        "style": payload.get("style"),
        "format": payload.get("format"),
        "rating": int(payload.get("rating", 5)),
        "created_at": now()
    }
    fb.append(entry)
    save(FEEDBACK_FILE, fb)

    # remove from queue
    q = load(QUEUE_FILE, [])
    q = [x for x in q if x.get("id") != payload.get("id")]
    save(QUEUE_FILE, q)

    return {"status":"approved","saved":entry}

@router.post("/reject")
def reject(payload: dict = Body(...)):
    fb = load(FEEDBACK_FILE, [])
    entry = {
        "id": payload.get("id"),
        "style": payload.get("style"),
        "format": payload.get("format"),
        "rating": int(payload.get("rating", 1)),
        "created_at": now()
    }
    fb.append(entry)
    save(FEEDBACK_FILE, fb)

    # remove from queue
    q = load(QUEUE_FILE, [])
    q = [x for x in q if x.get("id") != payload.get("id")]
    save(QUEUE_FILE, q)

    return {"status":"rejected","saved":entry}
