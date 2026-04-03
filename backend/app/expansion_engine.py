import os
import json
from datetime import datetime

DATA_DIR = "backend/data"
EXPANSION_FILE = os.path.join(DATA_DIR, "expansion_outputs.json")

os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def build_expansion_pack(item):
    topic = item.get("topic", "")
    buyer = item.get("buyer", "")
    promise = item.get("promise", "")
    content = item.get("content", "")
    niche = item.get("niche", "")
    tone = item.get("tone", "")

    hooks = [
        f"How {buyer or 'creators'} can use {topic} to {promise}",
        f"Nobody is talking about this {topic} angle yet",
        f"Use this {topic} method before everyone copies it"
    ]

    youtube = {
        "title": f"{topic} | Full Breakdown",
        "description": f"{topic}\n\nFor: {buyer}\nPromise: {promise}\nNiche: {niche}\nTone: {tone}",
        "outline": [
            f"What {topic} is",
            f"Why it matters for {buyer or 'creators'}",
            f"How to use it to {promise}",
            "Simple execution steps",
            "Common mistakes to avoid"
        ]
    }

    pdf = {
        "title": topic,
        "subtitle": f"For {buyer}" if buyer else "",
        "summary": content[:1200] if content else f"A practical guide for {buyer} to {promise}.",
        "sections": [
            "Overview",
            "Why it works",
            "Execution plan",
            "Best practices",
            "Next steps"
        ]
    }

    story = {
        "comic_concept": f"A visual story world built around: {topic}",
        "anime_concept": f"An anime-style progression arc based on {topic}",
        "film_pitch": f"A documentary or explainer film around {topic}",
        "game_pitch": f"A progression-based game loop inspired by {topic}"
    }

    pack = {
        "topic": topic,
        "created_at": datetime.utcnow().isoformat(),
        "tiktok": {
            "hooks": hooks,
            "caption": f"{topic} for {buyer}. {promise}",
            "short_script": f"Today we're breaking down {topic}. Here's how {buyer or 'creators'} can use it to {promise}."
        },
        "youtube": youtube,
        "pdf": pdf,
        "storyworld": story
    }
    return pack

def save_expansion_pack(pack):
    rows = load_json(EXPANSION_FILE, [])
    rows.append(pack)
    save_json(EXPANSION_FILE, rows)
    return pack

def get_expansion_history():
    return load_json(EXPANSION_FILE, [])
