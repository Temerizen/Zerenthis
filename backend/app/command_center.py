from fastapi import APIRouter, Body
from datetime import datetime, timezone
import uuid
import random

router = APIRouter(prefix="/api/command", tags=["command"])

def _now():
    return datetime.now(timezone.utc).isoformat()

CHARACTER_ARCHETYPES = [
    ("Leader", "confident but secretly insecure"),
    ("Clown", "funny but underestimated"),
    ("Villain", "manipulative and strategic"),
    ("Lover", "emotional and impulsive"),
    ("Wildcard", "unpredictable chaos"),
]

FORMATS = [
    "dating show",
    "survival island",
    "high school drama",
    "reality competition",
    "mafia betrayal",
]

OBJECT_STYLES = [
    "fruit",
    "animals",
    "robots",
    "food",
    "household objects"
]

def generate_characters(style):
    names = ["Alpha", "Nova", "Zara", "Blitz", "Milo"]
    chars = []
    for i in range(3):
        role, trait = random.choice(CHARACTER_ARCHETYPES)
        chars.append({
            "name": f"{style.capitalize()} {names[i]}",
            "role": role,
            "personality": trait
        })
    return chars

def generate_episode(prompt):
    style = random.choice(OBJECT_STYLES)
    format_type = random.choice(FORMATS)
    characters = generate_characters(style)

    hook = f"{style.capitalize()} {format_type} is already getting messy..."
    
    scenes = [
        f"{characters[0]['name']} enters and immediately causes tension.",
        f"{characters[1]['name']} flirts but gets rejected.",
        f"{characters[2]['name']} reveals a secret alliance.",
        "Everything escalates into drama.",
        "Cliffhanger ending."
    ]

    dialogue = [
        f"{characters[0]['name']}: 'You think you can trust them?'",
        f"{characters[1]['name']}: 'I came here to win, not play safe.'",
        f"{characters[2]['name']}: 'You have no idea what’s coming.'"
    ]

    return {
        "format": format_type,
        "style": style,
        "characters": characters,
        "hook": hook,
        "scenes": scenes,
        "dialogue": dialogue,
        "next_episode_hook": "Someone gets eliminated next episode."
    }

@router.post("/run")
def run_command(payload: dict = Body(...)):
    prompt = (payload.get("prompt") or "").strip()

    if not prompt:
        return {"status": "error", "error": "prompt is required"}

    episodes = [generate_episode(prompt) for _ in range(2)]

    return {
        "status": "ok",
        "phase": "viral story engine",
        "job_id": f"cmd_{uuid.uuid4().hex[:10]}",
        "created_at": _now(),
        "result": {
            "title": f"Viral Story Series: {prompt}",
            "summary": "Character-driven viral episode concepts designed for short-form domination.",
            "content": episodes,
            "next_action": "Pick one episode, generate visuals + voice, and post immediately."
        }
    }
