from fastapi import APIRouter, Body
from datetime import datetime, timezone
from pathlib import Path
import uuid, random, json

router = APIRouter(prefix="/api/command", tags=["command"])

BASE = Path(__file__).resolve().parents[2]
DATA = BASE / "backend/data"
OUT = BASE / "backend/outputs"

DATA.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

APPROVAL_FILE = DATA / "approvals.json"

def now():
    return datetime.now(timezone.utc).isoformat()

def load(path, default):
    return json.loads(path.read_text()) if path.exists() else default

def save(path, data):
    path.write_text(json.dumps(data, indent=2))

# --- TREND DNA ---
HOOKS = [
    "This went from normal to chaos instantly",
    "Nobody was ready for this",
    "This is the most chaotic episode yet",
    "You won't believe what happens next",
    "This might be the funniest idea ever"
]

STYLES = ["fruit","animals","robots","fast food","objects"]
FORMATS = ["dating show","elimination show","chaos reality show","sitcom","competition"]
TWISTS = ["betrayal","shock elimination","secret alliance","public humiliation"]

def generate_candidate(prompt):
    style = random.choice(STYLES)
    fmt = random.choice(FORMATS)

    title = f"{style.capitalize()} {fmt}"
    hook = random.choice(HOOKS)
    twist = random.choice(TWISTS)

    dialogue = [
        "I didn't come here to play safe.",
        "You're not ready for this.",
        "This is getting ridiculous.",
    ]

    score = score_candidate(hook, twist, style)

    return {
        "id": uuid.uuid4().hex[:8],
        "title": title,
        "hook": hook,
        "twist": twist,
        "style": style,
        "format": fmt,
        "dialogue": dialogue,
        "score": score
    }

def score_candidate(hook, twist, style):
    base = random.uniform(6,9)

    if "chaos" in hook.lower(): base += 0.5
    if twist in ["betrayal","shock elimination"]: base += 0.5
    if style in ["fruit","fast food","objects"]: base += 0.5

    return round(min(base,10),2)

def taste_gate(candidates):
    return [c for c in candidates if c["score"] >= 7.5]

def evolve(prompt):
    pool = [generate_candidate(prompt) for _ in range(10)]
    pool = taste_gate(pool)

    if not pool:
        pool = [generate_candidate(prompt) for _ in range(5)]

    pool = sorted(pool, key=lambda x: x["score"], reverse=True)
    return pool[0], pool[1:3]

# --- MULTI MEDIA EXPANSION ---
def expand_media(winner):

    return {
        "tiktok": {
            "episode": winner["title"],
            "hook": winner["hook"]
        },
        "youtube": {
            "long_form": f"{winner['title']} full episode concept"
        },
        "podcast": {
            "topic": f"Discussion inside {winner['title']}"
        },
        "comic": {
            "plot": f"Story arc based on {winner['twist']}"
        },
        "game": {
            "concept": f"Interactive {winner['format']} game with eliminations"
        },
        "series_arc": [
            "Episode 1: intro chaos",
            "Episode 2: alliances",
            "Episode 3: betrayal",
            "Episode 4: elimination",
            "Episode 5: twist escalation"
        ]
    }

@router.post("/run")
def run(payload: dict = Body(...)):
    prompt = payload.get("prompt","")

    winner, alts = evolve(prompt)
    media = expand_media(winner)

    approvals = load(APPROVAL_FILE, [])
    winner["approval_bias"] = len(approvals)

    file = f"{uuid.uuid4().hex[:6]}.json"
    (OUT / file).write_text(json.dumps({
        "winner": winner,
        "media": media
    }, indent=2))

    return {
        "status":"ok",
        "phase":"mega sweep A",
        "result":{
            "title": winner["title"],
            "summary": "Top-tier filtered and expanded content",
            "file": f"/api/file/{file}"
        },
        "winner": winner,
        "media": media
    }

@router.post("/approve")
def approve(payload: dict = Body(...)):
    approvals = load(APPROVAL_FILE, [])
    approvals.append(payload)
    save(APPROVAL_FILE, approvals)
    return {"status":"saved"}
