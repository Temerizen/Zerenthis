from __future__ import annotations

import re
import textwrap
import uuid
from pathlib import Path
from typing import Dict, List

from gtts import gTTS
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
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
    promise_text = promise or f"get faster results with {topic}"
    tone = (tone or "Premium").lower()

    if tone == "aggressive":
        return [
            f"Stop scrolling. {topic} is where most people waste time.",
            f"They keep overcomplicating it and get nowhere.",
            f"Cut the noise. Focus on one move. Repeat it.",
            f"If you want to {promise_text}, act now.",
        ]
    if tone == "motivational":
        return [
            f"If you feel behind in {topic}, this is your reset.",
            "You do not need perfection to move.",
            "You need one clear action and repetition.",
            f"If you want to {promise_text}, start today.",
        ]
    return [
        f"{topic} moves fast, but most people are still stuck.",
        "The reason is simple: too much noise, not enough structure.",
        "Keep it simple. Move fast. Repeat what works.",
        f"If you want to {promise_text}, this is the shift.",
    ]


def build_youtube_pack(topic: str, niche: str, tone: str, buyer: str, promise: str, bonus: str, notes: str) -> Dict:
    title = f"{topic.title()} for {buyer} | {promise or 'A Cleaner System'}"
    thumbnail = {
        "headline": f"STOP WASTING TIME ON {topic.upper()}",
        "subline": promise or "A cleaner way to move faster",
        "visual": "High contrast close-up, large emotional headline, dark background, cyan accent",
        "colors": "Black, cyan, white, electric purple accents",
    }
    description = (
        f"In this video, we break down a sharper way to approach {topic}. "
        f"If you are a {buyer.lower()} and want to {promise or f'get results faster with {topic}'}, "
        "this gives you a more practical framework."
    )
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

LONG-FORM SCRIPT:

Hook:
If you are trying to improve at {topic} and it still feels messy, this video simplifies the path.

Why Most People Stay Stuck:
Most people collect information instead of building a repeatable system.

The Core Shift:
The win is not doing more. It is doing fewer things with better structure.

Framework:
1. Define the exact result.
2. Remove distractions.
3. Build a repeatable loop.
4. Improve after action.

Common Mistakes:
- trying too much at once
- confusing motivation with discipline
- polishing the wrong things

CTA:
Use this framework today and start building proof.

BONUS:
- {bonus or "Prompt pack"}
- shorts spin-offs
- extra CTA variants

NOTES:
{notes or "Keep it premium, direct, and useful."}
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


def _bg_color(index: int):
    palette = [
        (8, 12, 22),
        (14, 20, 34),
        (12, 26, 40),
        (24, 14, 42),
        (10, 22, 20),
    ]
    return palette[index % len(palette)]


def _draw_slide(text: str, image_path: Path, topic: str, index: int, cta: bool = False) -> None:
    img = Image.new("RGB", SIZE, color=_bg_color(index))
    draw = ImageDraw.Draw(img)

    width, height = SIZE
    title_font = _safe_font(32)
    topic_font = _safe_font(22)
    body_font = _safe_font(52 if not cta else 60)
    small_font = _safe_font(24)

    draw.rounded_rectangle((40, 42, width - 40, 68), radius=12, fill=(0, 229, 255))
    draw.rounded_rectangle((40, height - 94, width - 40, height - 64), radius=12, fill=(124, 92, 255))

    draw.text((54, 88), "ZERENTHIS SHORTS FACTORY", fill=(238, 248, 255), font=title_font)
    draw.text((54, 132), topic.upper(), fill=(130, 224, 255), font=topic_font)

    wrapped = textwrap.fill(text, width=16)
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=body_font, spacing=14)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (width - tw) // 2
    y = (height - th) // 2 - 40

    draw.multiline_text((x + 4, y + 4), wrapped, fill=(0, 0, 0), font=body_font, spacing=14, align="center")
    draw.multiline_text((x, y), wrapped, fill=(255, 255, 255), font=body_font, spacing=14, align="center")

    footer = "Follow for more" if cta else "Generated by Zerenthis"
    draw.text((54, height - 138), footer, fill=(220, 226, 240), font=small_font)

    img.save(str(image_path))


def _draw_thumbnail(topic: str, promise: str, image_path: Path) -> None:
    img = Image.new("RGB", (1280, 720), color=(8, 10, 18))
    draw = ImageDraw.Draw(img)

    big_font = _safe_font(78)
    mid_font = _safe_font(38)
    small_font = _safe_font(24)

    draw.rectangle((0, 0, 1280, 120), fill=(0, 229, 255))
    draw.text((40, 36), "ZERENTHIS", fill=(10, 18, 24), font=mid_font)

    headline = "STOP DOING THIS"
    subline = promise or f"Fix your {topic} flow"

    draw.text((48, 180), headline, fill=(255, 255, 255), font=big_font)
    draw.text((48, 300), topic.upper(), fill=(130, 224, 255), font=big_font)
    draw.text((48, 430), subline, fill=(230, 240, 255), font=mid_font)
    draw.text((48, 640), "High contrast • bold text • fast hook", fill=(180, 190, 210), font=small_font)

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
    cta_line = "Follow for more systems like this."
    voice_text = " ".join(script_lines + [cta_line])

    slug = _slugify(topic)
    uid = uuid.uuid4().hex[:8]

    audio_path = OUTPUT_DIR / f"{slug}-{uid}.mp3"
    _make_audio(voice_text, audio_path)

    audio = AudioFileClip(str(audio_path))
    all_lines = script_lines + [cta_line]
    per_slide = max(audio.duration / len(all_lines), 1.6)

    clips = []
    for idx, line in enumerate(all_lines):
        image_path = OUTPUT_DIR / f"{slug}-{uid}-{idx}.png"
        _draw_slide(line, image_path, topic, idx, cta=(idx == len(all_lines) - 1))
        clip = ImageClip(str(image_path)).set_duration(per_slide)
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose").set_audio(audio)

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

    thumbnail_name = f"{slug}-thumb-{uid}.png"
    thumbnail_path = OUTPUT_DIR / thumbnail_name
    _draw_thumbnail(topic, promise, thumbnail_path)

    file_url = f"{base_url}/api/file/{out_name}" if base_url else f"/api/file/{out_name}"
    thumb_url = f"{base_url}/api/file/{thumbnail_name}" if base_url else f"/api/file/{thumbnail_name}"

    return {
        "status": "done",
        "mode": "shorts",
        "title": f"{topic.title()} Shorts Pack",
        "script_lines": all_lines,
        "subtitles": "\n".join(all_lines),
        "file_name": out_name,
        "file_url": file_url,
        "preview_url": file_url,
        "thumbnail_file_name": thumbnail_name,
        "thumbnail_url": thumb_url,
    }
