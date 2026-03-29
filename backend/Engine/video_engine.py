from __future__ import annotations

import math
import re
import textwrap
import uuid
from pathlib import Path
from typing import Dict, List

import numpy as np
from gtts import gTTS
from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    VideoFileClip,
    concatenate_videoclips,
)
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "data" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SIZE = (720, 1280)
FPS = 24


def _slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value or "zerenthis-video"


def _safe_font(size: int):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size=size)
    except Exception:
        return ImageFont.load_default()


def build_shorts_script(topic: str, tone: str, promise: str) -> List[str]:
    promise_text = promise or f"win faster with {topic}"
    tone = (tone or "Premium").lower()

    if tone == "aggressive":
        return [
            f"Stop scrolling. {topic} is moving faster than most people can keep up.",
            f"Most people stay broke because they overcomplicate {topic}.",
            f"Here is the shift: cut the noise, focus on one move, and repeat it.",
            f"If you want to {promise_text}, move now, not later.",
        ]

    if tone == "motivational":
        return [
            f"If you feel behind in {topic}, that does not mean you are finished.",
            f"Most people lose because they never turn intention into repetition.",
            f"Pick one clear action, do it today, and keep stacking proof.",
            f"If you want to {promise_text}, start with motion, not perfection.",
        ]

    return [
        f"{topic} is changing faster than most people realize.",
        f"The people who win do not chase everything. They master one clear move.",
        f"Keep it simple, act fast, and keep showing up.",
        f"If you want to {promise_text}, this is where momentum starts.",
    ]


def build_youtube_pack(topic: str, niche: str, tone: str, buyer: str, promise: str, bonus: str, notes: str) -> Dict:
    title = f"{topic.title()} for {buyer} | {promise or 'A Better System'}"
    thumbnail = {
        "headline": f"STOP WASTING TIME ON {topic.upper()}",
        "subline": promise or "A cleaner way to move faster",
        "visual": "High contrast close-up, bold text, one main emotional idea",
        "colors": "Black, cyan, white, electric purple accents",
    }
    description = (
        f"In this video, we break down a sharper way to approach {topic}. "
        f"If you are a {buyer.lower()} and want to {promise or f'get results faster with {topic}'}, "
        "this guide gives you a practical framework to follow."
    )
    sections = [
        "Hook",
        "Why most people stay stuck",
        "The core shift",
        "Step-by-step framework",
        "Common mistakes",
        "Closing CTA",
    ]
    script = f"""
TITLE:
{title}

THUMBNAIL:
Headline: {thumbnail["headline"]}
Subline: {thumbnail["subline"]}
Visual Direction: {thumbnail["visual"]}
Colors: {thumbnail["colors"]}

DESCRIPTION:
{description}

CHAPTERS:
- {sections[0]}
- {sections[1]}
- {sections[2]}
- {sections[3]}
- {sections[4]}
- {sections[5]}

LONG-FORM SCRIPT:

Hook:
If you are trying to improve at {topic} and nothing feels like it is clicking, this video will simplify the path.

Why Most People Stay Stuck:
Most people collect information instead of building a repeatable system. In {niche}, that creates overwhelm, hesitation, and wasted time.

The Core Shift:
The win is not doing more. It is doing fewer things with better structure and better repetition.

Step-by-Step Framework:
Step 1: Define the exact result.
Step 2: Remove distractions.
Step 3: Build a repeatable process.
Step 4: Review and improve after action, not before it.

Common Mistakes:
Trying to do too much at once.
Confusing motivation with discipline.
Chasing aesthetics before outcomes.

Closing CTA:
If this helped, use this framework today and keep building proof.

BONUS IDEAS:
- {bonus or "Prompt pack"}
- Expansion episode ideas
- Shorts spin-offs
- CTA variants

NOTES:
{notes or "Keep the video premium, clear, and direct."}
""".strip()

    return {
        "status": "done",
        "mode": "youtube",
        "title": title,
        "thumbnail": thumbnail,
        "description": description,
        "script": script,
    }


def _make_audio(script_text: str, audio_path: Path) -> None:
    tts = gTTS(script_text, lang="en", slow=False)
    tts.save(str(audio_path))


def _draw_slide(text: str, image_path: Path, topic: str, index: int) -> None:
    img = Image.new("RGB", SIZE, color=(6 + index * 8, 10 + index * 6, 20 + index * 10))
    draw = ImageDraw.Draw(img)

    width, height = SIZE

    # accent glow bar
    draw.rounded_rectangle((40, 46, width - 40, 66), radius=10, fill=(0, 229, 255))
    draw.rounded_rectangle((40, height - 94, width - 40, height - 64), radius=10, fill=(124, 92, 255))

    title_font = _safe_font(34)
    body_font = _safe_font(48)
    small_font = _safe_font(24)

    draw.text((54, 92), "ZERENTHIS SHORTS FACTORY", fill=(230, 246, 255), font=title_font)
    draw.text((54, 134), topic.upper(), fill=(130, 224, 255), font=small_font)

    wrapped = textwrap.fill(text, width=18)
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=body_font, spacing=12)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (width - tw) // 2
    y = (height - th) // 2 - 20

    # shadow
    draw.multiline_text((x + 3, y + 3), wrapped, fill=(0, 0, 0), font=body_font, spacing=12, align="center")
    draw.multiline_text((x, y), wrapped, fill=(255, 255, 255), font=body_font, spacing=12, align="center")

    draw.text((54, height - 138), "Generated by Zerenthis", fill=(215, 220, 240), font=small_font)

    img.save(str(image_path))


def build_shorts_video(
    *,
    topic: str,
    tone: str,
    promise: str,
    duration_seconds: int,
    base_url: str,
) -> dict:
    script_lines = build_shorts_script(topic, tone, promise)
    voice_text = " ".join(script_lines)

    slug = _slugify(topic)
    uid = uuid.uuid4().hex[:8]

    audio_path = OUTPUT_DIR / f"{slug}-{uid}.mp3"
    _make_audio(voice_text, audio_path)

    audio = AudioFileClip(str(audio_path))
    line_count = max(1, len(script_lines))
    per_slide = max(audio.duration / line_count, 1.8)

    image_paths: List[Path] = []
    clips = []

    for idx, line in enumerate(script_lines):
        image_path = OUTPUT_DIR / f"{slug}-{uid}-{idx}.png"
        image_paths.append(image_path)
        _draw_slide(line, image_path, topic, idx)

        clip = ImageClip(str(image_path)).set_duration(per_slide)
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose").set_audio(audio)

    # Optional trim/extend target
    target = max(int(duration_seconds or 0), 0)
    if target and video.duration > target:
        video = video.subclip(0, target)

    out_name = f"{slug}-shorts-{uid}.mp4"
    out_path = OUTPUT_DIR / out_name

    video.write_videofile(
        str(out_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=2,
        verbose=False,
        logger=None,
    )

    file_url = f"{base_url}/api/file/{out_name}"
    subtitle_text = "\n".join(script_lines)

    return {
        "status": "done",
        "mode": "shorts",
        "title": f"{topic.title()} Shorts Pack",
        "script_lines": script_lines,
        "subtitles": subtitle_text,
        "file_name": out_name,
        "file_url": file_url,
        "preview_url": file_url,
    }
