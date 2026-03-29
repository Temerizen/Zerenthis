from __future__ import annotations

import re
import textwrap
import uuid
from pathlib import Path
from typing import Dict, List

from gtts import gTTS
from moviepy.editor import AudioFileClip, CompositeVideoClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "data" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SIZE = (720, 1280)
FPS = 24


def _slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value or "zerenthis-video"


def _font(size: int):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size=size)
    except Exception:
        return ImageFont.load_default()


def build_shorts_script(topic: str, tone: str, promise: str) -> List[str]:
    promise_text = promise or f"improve faster with {topic}"
    tone = (tone or "Premium").lower()

    if tone == "aggressive":
        return [
            f"Stop wasting time on {topic}.",
            f"Most people fail because they overcomplicate everything.",
            "The fix is simple: choose one move, repeat it, and cut the noise.",
            f"If you want to {promise_text}, start today.",
        ]
    if tone == "motivational":
        return [
            f"If you feel behind with {topic}, you are not out of the game.",
            "Momentum starts with one clean action, not a perfect plan.",
            "Do the simple version first, then improve after proof.",
            f"If you want to {promise_text}, movement beats doubt.",
        ]
    return [
        f"{topic} is moving faster than most people realize.",
        "The winners are not doing everything. They are doing the right few things repeatedly.",
        "Keep it simple, move fast, and stay consistent.",
        f"If you want to {promise_text}, this is the direction.",
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

STRUCTURE:
1. Hook
2. Why people stay stuck
3. The core shift
4. Framework
5. Mistakes
6. CTA

LONG-FORM SCRIPT:
If you're trying to improve at {topic} and it still feels messy, this video is built to simplify the path.
Most people stay stuck because they collect ideas instead of using a system.
The better move is clarity, repetition, and cleaner execution.

BONUSES:
- {bonus or 'Prompt pack'}
- spin-off shorts
- CTA ideas
- thumbnail variants

NOTES:
{notes or 'Keep it premium and direct.'}
""".strip()

    return {
        "status": "done",
        "mode": "youtube",
        "title": title,
        "script": script,
    }


def _draw_slide(text: str, image_path: Path, topic: str, index: int, total: int):
    width, height = SIZE
    bg_colors = [
        (5, 10, 20),
        (10, 18, 32),
        (18, 16, 42),
        (8, 20, 28),
    ]
    img = Image.new("RGB", SIZE, color=bg_colors[index % len(bg_colors)])
    draw = ImageDraw.Draw(img)

    title_font = _font(34)
    body_font = _font(48)
    small_font = _font(22)
    cta_font = _font(28)

    # top bar
    draw.rounded_rectangle((36, 36, width - 36, 62), radius=12, fill=(0, 229, 255))
    # progress bar
    progress = int((index + 1) / max(total, 1) * (width - 72))
    draw.rounded_rectangle((36, 1120, width - 36, 1142), radius=10, fill=(50, 60, 90))
    draw.rounded_rectangle((36, 1120, 36 + progress, 1142), radius=10, fill=(124, 92, 255))

    draw.text((50, 84), "ZERENTHIS SHORTS", fill=(230, 245, 255), font=title_font)
    draw.text((50, 128), topic.upper(), fill=(130, 224, 255), font=small_font)

    wrapped = textwrap.fill(text, width=18)
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=body_font, spacing=10)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (width - tw) // 2
    y = (height - th) // 2 - 20

    draw.multiline_text((x + 3, y + 3), wrapped, fill=(0, 0, 0), font=body_font, spacing=10, align="center")
    draw.multiline_text((x, y), wrapped, fill=(255, 255, 255), font=body_font, spacing=10, align="center")

    draw.text((50, 1180), "Follow for more", fill=(220, 230, 240), font=cta_font)

    img.save(str(image_path))


def _draw_thumbnail(topic: str, promise: str, image_path: Path):
    width, height = 1280, 720
    img = Image.new("RGB", (width, height), color=(7, 10, 18))
    draw = ImageDraw.Draw(img)

    big_font = _font(72)
    small_font = _font(34)

    draw.rounded_rectangle((40, 40, width - 40, 78), radius=12, fill=(0, 229, 255))
    draw.rounded_rectangle((50, 120, width - 50, height - 50), radius=24, outline=(124, 92, 255), width=6)

    headline = f"STOP WASTING TIME ON {topic.upper()}"
    wrapped = textwrap.fill(headline, width=16)
    draw.multiline_text((80, 180), wrapped, fill=(255, 255, 255), font=big_font, spacing=8)

    sub = promise or "A faster way to improve"
    draw.text((80, 590), sub, fill=(160, 220, 255), font=small_font)

    img.save(str(image_path))


def build_shorts_video(
    *,
    topic: str,
    tone: str,
    promise: str,
    duration_seconds: int,
    base_url: str,
) -> Dict:
    script_lines = build_shorts_script(topic, tone, promise)
    voice_text = " ".join(script_lines)

    slug = _slugify(topic)
    uid = uuid.uuid4().hex[:8]

    audio_path = OUTPUT_DIR / f"{slug}-{uid}.mp3"
    gTTS(voice_text, lang="en", slow=False).save(str(audio_path))
    audio = AudioFileClip(str(audio_path))

    total = len(script_lines)
    per_slide = max(audio.duration / max(total, 1), 1.8)

    clips = []
    for idx, line in enumerate(script_lines):
        image_path = OUTPUT_DIR / f"{slug}-{uid}-{idx}.png"
        _draw_slide(line, image_path, topic, idx, total)
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

    thumb_name = f"{slug}-thumb-{uid}.png"
    thumb_path = OUTPUT_DIR / thumb_name
    _draw_thumbnail(topic, promise, thumb_path)

    file_url = f"{base_url}/api/file/{out_name}"
    thumb_url = f"{base_url}/api/file/{thumb_name}"

    return {
        "status": "done",
        "mode": "shorts",
        "title": f"{topic.title()} Shorts Pack",
        "script_lines": script_lines,
        "subtitles": "\n".join(script_lines),
        "file_name": out_name,
        "file_url": file_url,
        "preview_url": file_url,
        "thumbnail_file_name": thumb_name,
        "thumbnail_url": thumb_url,
    }


def build_shorts_batch(
    *,
    topic: str,
    tone: str,
    promise: str,
    duration_seconds: int,
    base_url: str,
    count: int = 3,
) -> Dict:
    items = []
    for i in range(max(1, min(count, 10))):
        result = build_shorts_video(
            topic=f"{topic} {i+1}",
            tone=tone,
            promise=promise,
            duration_seconds=duration_seconds,
            base_url=base_url,
        )
        items.append(result)

    return {
        "status": "done",
        "mode": "shorts_batch",
        "count": len(items),
        "items": items,
    }
