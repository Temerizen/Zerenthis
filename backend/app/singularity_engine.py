from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime, timezone
import json
import textwrap
import re
import uuid

from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
OUTPUT_DIR = DATA_DIR / "outputs"
DNA_DIR = DATA_DIR / "story_dna"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DNA_DIR.mkdir(parents=True, exist_ok=True)

class SingularityRequest(BaseModel):
    idea: str
    tone: str = "cinematic"
    audience: str = "general"
    mode: str = "viral"
    duration_seconds: int = 30
    visual_style: str = "cinematic"
    title_hint: str = ""
    girlfriend_mode: bool = False

def now():
    return datetime.now(timezone.utc).isoformat()

def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "untitled"

def build_story_dna(req: SingularityRequest) -> dict:
    base_theme = "love and connection" if req.girlfriend_mode else "transformation and momentum"
    tone_map = {
        "cinematic": "sweeping, emotional, visually rich",
        "romantic": "warm, intimate, affectionate",
        "viral": "hooky, immediate, curiosity-driven",
        "dark": "moody, mysterious, intense",
        "cute": "gentle, playful, wholesome"
    }
    story_tone = tone_map.get(req.tone.lower(), req.tone)

    title = req.title_hint.strip() if req.title_hint.strip() else req.idea.strip()

    protagonist = "a loving narrator" if req.girlfriend_mode else "an ambitious creator"
    secondary = "his favorite person" if req.girlfriend_mode else "the audience"
    conflict = (
        "finding a beautiful way to express love through moving images"
        if req.girlfriend_mode else
        "turning raw imagination into unforgettable entertainment"
    )

    dna = {
        "created_at": now(),
        "idea": req.idea,
        "title": title,
        "audience": req.audience,
        "mode": req.mode,
        "tone": req.tone,
        "visual_style": req.visual_style,
        "girlfriend_mode": req.girlfriend_mode,
        "world": {
            "setting": "a cinematic digital universe of emotion, memory, and momentum",
            "theme": base_theme,
            "visual_identity": req.visual_style,
            "audio_identity": "soft emotional score with clear intimate narration" if req.girlfriend_mode else "bold modern score with crisp motivating narration"
        },
        "characters": [
            {
                "name": "Narrator",
                "role": protagonist,
                "voice_style": "soft and affectionate" if req.girlfriend_mode else "confident and inspiring"
            },
            {
                "name": "Listener",
                "role": secondary,
                "voice_style": "silent emotional focal point"
            }
        ],
        "story_arc": {
            "hook": "A single idea can become a whole universe." if not req.girlfriend_mode else "I wanted to make something beautiful just for you.",
            "conflict": conflict,
            "turn": "The imagination begins shaping images, feeling, and motion.",
            "ending": "The moment becomes a memory you can watch again."
        },
        "format_targets": [
            "video",
            "short_form",
            "podcast",
            "comic",
            "novel",
            "game_concept"
        ]
    }
    return dna

def build_video_script(dna: dict, req: SingularityRequest) -> str:
    if req.girlfriend_mode:
        script = f"""
        {dna['story_arc']['hook']}
        This started as a simple thought about you, and then it grew into a little world.
        In that world, every scene is warm, every light feels soft, and every second says what words sometimes miss.
        You are the reason the story feels alive.
        So this is more than a video.
        It is a small moving memory, made to wrap around your heart.
        """
    else:
        script = f"""
        {dna['story_arc']['hook']}
        What begins as one spark can become a full entertainment universe.
        Characters appear. Worlds sharpen. Emotion gets a shape.
        Stories turn into scenes, scenes turn into motion, and motion turns into something people remember.
        This is what happens when imagination stops waiting and starts building.
        """
    return " ".join(line.strip() for line in script.splitlines() if line.strip())

def save_story_dna(dna: dict) -> str:
    dna_id = f"{slugify(dna['title'])}_{uuid.uuid4().hex[:6]}"
    path = DNA_DIR / f"{dna_id}.json"
    path.write_text(json.dumps(dna, indent=2, ensure_ascii=False), encoding="utf-8")
    return path.name

def make_frame(text: str, title: str, out_path: Path, width: int = 1080, height: int = 1920) -> None:
    img = Image.new("RGB", (width, height), color=(10, 12, 18))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 64)
        font_body = ImageFont.truetype("arial.ttf", 42)
    except Exception:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()

    margin = 80
    title_wrapped = textwrap.fill(title, width=18)
    body_wrapped = textwrap.fill(text, width=26)

    draw.multiline_text((margin, 180), title_wrapped, font=font_title, fill=(255, 255, 255), spacing=10)
    draw.rounded_rectangle((70, 520, width - 70, height - 220), radius=40, outline=(80, 180, 255), width=4)
    draw.multiline_text((110, 600), body_wrapped, font=font_body, fill=(220, 230, 245), spacing=14)

    img.save(out_path)

def render_video(title: str, script: str, video_slug: str) -> tuple[str, str]:
    audio_path = OUTPUT_DIR / f"{video_slug}.mp3"
    tts = gTTS(text=script, lang="en")
    tts.save(str(audio_path))

    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', script) if s.strip()]
    if not sentences:
        sentences = [script]

    image_paths = []
    for idx, sentence in enumerate(sentences[:8], start=1):
        img_path = OUTPUT_DIR / f"{video_slug}_frame_{idx}.png"
        make_frame(sentence, title, img_path)
        image_paths.append(img_path)

    audio_clip = AudioFileClip(str(audio_path))
    total_duration = max(audio_clip.duration, 6)
    per_image = total_duration / max(len(image_paths), 1)

    clips = [ImageClip(str(p)).set_duration(per_image) for p in image_paths]
    video = concatenate_videoclips(clips, method="compose").set_audio(audio_clip)

    mp4_path = OUTPUT_DIR / f"{video_slug}.mp4"
    video.write_videofile(
        str(mp4_path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )

    audio_clip.close()
    video.close()
    for clip in clips:
        clip.close()

    return mp4_path.name, audio_path.name

@router.post("/api/singularity/create")
def create_singularity(req: SingularityRequest):
    try:
        dna = build_story_dna(req)
        dna_file = save_story_dna(dna)

        script = build_video_script(dna, req)
        title = dna["title"]
        video_slug = f"{slugify(title)}_{uuid.uuid4().hex[:6]}"
        video_file, audio_file = render_video(title, script, video_slug)

        return {
            "ok": True,
            "mode": "core_singularity",
            "title": title,
            "story_dna_file": f"/api/singularity/file/{dna_file}",
            "script": script,
            "video_file": f"/api/file/{video_file}",
            "audio_file": f"/api/file/{audio_file}",
            "next_expansions": [
                "podcast",
                "comic",
                "novel",
                "game_concept"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"singularity_error: {str(e)}")

@router.get("/api/singularity/file/{name:path}")
def get_singularity_file(name: str):
    safe_name = Path(name).name
    target = DNA_DIR / safe_name
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="story dna file not found")
    return FileResponse(str(target), filename=safe_name)
