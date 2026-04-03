from fastapi import APIRouter, Body
from datetime import datetime, timezone
import uuid, random, json
from pathlib import Path

router = APIRouter(prefix="/api/command", tags=["command"])

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def _now():
    return datetime.now(timezone.utc).isoformat()

def _slug(s):
    return "".join(c.lower() if c.isalnum() else "_" for c in s)[:60]

# --- TREND PATTERNS (SIMULATED INTERNET DNA) ---
HOOK_PATTERNS = [
    "Nobody expected this to happen...",
    "This got out of control instantly",
    "This might be the funniest thing on the internet",
    "This went from normal to chaos in seconds",
    "You won’t believe what happens next",
    "This is why nobody talks about this",
]

FORMATS = [
    "dating show chaos",
    "elimination drama",
    "reality show parody",
    "absurd sitcom",
    "fake documentary",
]

STYLES = [
    "fruit", "animals", "robots", "fast food", "objects"
]

TWISTS = [
    "betrayal", "secret alliance", "shock elimination",
    "public embarrassment", "unexpected confession"
]

ARCHETYPES = [
    ("leader", "confident but fragile"),
    ("villain", "manipulative and charming"),
    ("clown", "funny but chaotic"),
    ("lover", "emotional and dramatic"),
    ("wildcard", "unpredictable energy"),
]

def generate_characters(style):
    base = ["Nova","Blitz","Zara","Milo","Echo","Vex"]
    random.shuffle(base)
    chars = []
    for i in range(4):
        role, trait = random.choice(ARCHETYPES)
        chars.append({
            "name": f"{style.capitalize()} {base[i]}",
            "role": role,
            "personality": trait
        })
    return chars

def generate_candidate(prompt, parent=None):
    style = parent["style"] if parent and random.random() < 0.6 else random.choice(STYLES)
    fmt = parent["format"] if parent and random.random() < 0.6 else random.choice(FORMATS)
    chars = generate_characters(style)
    hook = random.choice(HOOK_PATTERNS)
    twist = random.choice(TWISTS)

    scenes = [
        f"{chars[0]['name']} causes immediate tension",
        f"{chars[1]['name']} challenges them",
        f"{chars[2]['name']} says something insane",
        f"Twist: {twist}",
        "Cliffhanger ending"
    ]

    dialogue = [
        f"{chars[0]['name']}: 'I didn’t come here to play safe.'",
        f"{chars[1]['name']}: 'You’re not ready for this.'",
        f"{chars[2]['name']}: 'This is getting ridiculous.'",
    ]

    score = score_candidate(hook, scenes, dialogue, style, fmt)

    return {
        "id": uuid.uuid4().hex[:8],
        "title": f"{style} {fmt}",
        "style": style,
        "format": fmt,
        "hook": hook,
        "characters": chars,
        "scenes": scenes,
        "dialogue": dialogue,
        "score": score
    }

def score_candidate(hook, scenes, dialogue, style, fmt):
    text = (hook + " ".join(scenes) + " ".join(dialogue)).lower()

    hook_score = 9 if "this" in hook.lower() else 6
    chaos = 9 if any(x in text for x in ["chaos","ridiculous","out of control"]) else 6
    meme = 8 if any(x in text for x in ["insane","funniest"]) else 5
    retention = 9 if "cliffhanger" in text else 6
    absurdity = 8 if style in ["fruit","fast food","objects"] else 6

    overall = round((hook_score*0.25 + chaos*0.2 + meme*0.15 + retention*0.2 + absurdity*0.2),2)

    return {
        "overall": overall,
        "hook": hook_score,
        "chaos": chaos,
        "meme": meme,
        "retention": retention,
        "absurdity": absurdity
    }

def evolve(prompt):
    population = [generate_candidate(prompt) for _ in range(6)]

    for _ in range(4):
        ranked = sorted(population, key=lambda x: x["score"]["overall"], reverse=True)
        best = ranked[:2]

        new_pop = best[:]
        while len(new_pop) < 6:
            parent = random.choice(best)
            new_pop.append(generate_candidate(prompt, parent))
        population = new_pop

    final = sorted(population, key=lambda x: x["score"]["overall"], reverse=True)
    return final[0], final[1:3]

@router.post("/run")
def run_command(payload: dict = Body(...)):
    prompt = payload.get("prompt", "")

    winner, alternatives = evolve(prompt)

    artifact = {
        "winner": winner,
        "alternatives": alternatives,
        "created_at": _now()
    }

    file_name = f"{_slug(prompt)}_{uuid.uuid4().hex[:6]}.json"
    path = OUTPUT_DIR / file_name
    path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    return {
        "status": "ok",
        "phase": "god sweep intelligence core",
        "result": {
            "title": winner["title"],
            "summary": "Top evolved viral concept selected.",
            "assets": [
                {"type":"concept","label":"Winner Concept","url":f"/api/file/{file_name}"}
            ],
            "next_action": "Turn this into a video immediately."
        },
        "winner": winner,
        "alternatives": alternatives
    }
