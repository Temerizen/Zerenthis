from __future__ import annotations

import uuid
from pathlib import Path
from typing import Dict, List

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def _safe_filename(text: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("_", "-", " ") else "_" for ch in text).strip().replace(" ", "_")

def build_shorts_script(topic: str, tone: str, promise: str) -> List[str]:
    promise_text = promise or f"improve faster with {topic}"
    tone = (tone or "Premium").lower().strip()
    topic = topic.strip()

    if tone == "aggressive":
        return [
            f"Stop scrolling if you want better results with {topic}.",
            f"Most people stay stuck because they make {topic} more complicated than it needs to be.",
            "Pick one tactic, repeat it daily, and cut everything that does not move the needle.",
            f"If you want to {promise_text}, start simple and start now.",
        ]
    if tone == "motivational":
        return [
            f"If {topic} feels overwhelming right now, that does not mean you are behind.",
            "Real momentum starts when you stop chasing perfect and commit to one clean move.",
            "Build proof first, then improve the system after you see what works.",
            f"If you want to {promise_text}, consistency will beat doubt every time.",
        ]
    return [
        f"Here is the simpler way to win with {topic}.",
        f"Most people consume more information about {topic} than they ever execute.",
        "The edge is choosing a small repeatable system and sticking to it long enough to compound.",
        f"If you want to {promise_text}, use this as your sign to move today.",
    ]

def _make_image(topic: str, lines: List[str], filename: str) -> str:
    path = OUTPUT_DIR / filename
    img = Image.new("RGB", (1080, 1920), color=(8, 12, 20))
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arial.ttf", 70)
        body_font = ImageFont.truetype("arial.ttf", 42)
        cta_font = ImageFont.truetype("arial.ttf", 48)
    except Exception:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        cta_font = ImageFont.load_default()

    draw.text((50, 70), topic.upper(), fill=(0, 229, 255), font=title_font)

    y = 260
    for line in lines:
        wrapped = [line[i:i+38] for i in range(0, len(line), 38)] or [""]
        for chunk in wrapped:
            draw.text((50, y), chunk, fill=(230, 240, 255), font=body_font)
            y += 72
        y += 20

    draw.text((50, 1740), "Download the execution pack", fill=(220, 230, 240), font=cta_font)
    img.save(path)
    return filename

def build_shorts_video(topic: str, tone: str, promise: str, duration_seconds: int = 35, base_url: str = "") -> Dict:
    script = build_shorts_script(topic, tone, promise)
    filename = f"{_safe_filename(topic)}_{uuid.uuid4().hex[:6]}.png"
    _make_image(topic, script, filename)
    file_url = f"{base_url}/api/file/{filename}" if base_url else f"/api/file/{filename}"
    return {
        "status": "completed",
        "mode": "shorts",
        "topic": topic,
        "script": script,
        "duration_seconds": duration_seconds,
        "file_name": filename,
        "file_url": file_url,
    }

def build_shorts_batch(**kwargs):
    count = int(kwargs.get("count", 3) or 3)
    topic = kwargs.get("topic", "AI")
    tone = kwargs.get("tone", "Premium")
    promise = kwargs.get("promise", "")
    duration_seconds = int(kwargs.get("duration_seconds", 35) or 35)
    base_url = kwargs.get("base_url", "")
    return [
        build_shorts_video(
            topic=f"{topic} Variation {i + 1}" if count > 1 else topic,
            tone=tone,
            promise=promise,
            duration_seconds=duration_seconds,
            base_url=base_url,
        )
        for i in range(count)
    ]

def build_youtube_pack(topic: str, niche: str, tone: str, buyer: str, promise: str, bonus: str, notes: str) -> Dict:
    title = f"{topic.title()} for {buyer} | {promise or 'A Better System'}"
    script = f"""
TITLE:
{title}

THUMBNAIL:
Headline: STOP WASTING TIME ON {topic.upper()}
Subline: {promise or 'A cleaner way to move faster'}
Colors: Black, cyan, white

DESCRIPTION:
A premium long-form YouTube pack for {buyer.lower()} in {niche.lower()}.

POSITIONING:
Primary audience: {buyer}
Core promise: {promise or f'Get better results with {topic}'}
Tone: {tone}
Suggested offer: low-ticket digital product + upsell bundle

STRUCTURE:
1. Hook
2. Why people stay stuck
3. The core shift
4. Framework
5. Mistakes
6. CTA

HOOK OPTIONS:
- Most people are making {topic} harder than it needs to be.
- If you have been stuck trying to win with {topic}, this is the reset.
- Here is the cleaner system for {buyer.lower()} who want real momentum.

CTA IDEAS:
- Download the companion execution pack.
- Grab the prompt bundle linked below.
- Use the checklist and templates to implement this faster.

NOTES:
{notes or 'Keep it premium and direct.'}
""".strip()

    return {
        "status": "completed",
        "mode": "youtube",
        "title": title,
        "script": script,
    }
