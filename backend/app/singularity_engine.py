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
from PIL import Image, ImageDraw, ImageFont, ImageFilter
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
    title = req.title_hint.strip() if req.title_hint.strip() else req.idea.strip()

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
            "setting": "a dreamy emotional universe made of memory, warmth, and gentle light" if req.girlfriend_mode else "a cinematic digital universe of momentum and imagination",
            "theme": "love, appreciation, tenderness, and emotional safety" if req.girlfriend_mode else "transformation and possibility",
            "visual_identity": req.visual_style,
            "audio_identity": "soft intimate narration with gentle emotional cadence" if req.girlfriend_mode else "clean cinematic narration"
        },
        "characters": [
            {
                "name": "Narrator",
                "role": "someone quietly in love" if req.girlfriend_mode else "an imaginative guide",
                "voice_style": "soft, affectionate, sincere" if req.girlfriend_mode else "clear, warm, cinematic"
            },
            {
                "name": "Beloved" if req.girlfriend_mode else "Audience",
                "role": "the emotional center of the story" if req.girlfriend_mode else "the witness to the transformation",
                "voice_style": "silent emotional focal point"
            }
        ],
        "story_arc": {
            "hook": "I wanted to make something beautiful just for you." if req.girlfriend_mode else "One idea can become a whole universe.",
            "middle": "The feeling grows into images, into light, into little moments that feel like they were always waiting to exist." if req.girlfriend_mode else "The idea sharpens into something people can see, hear, and remember.",
            "ending": "So if this feels warm, that is because it was made from real feeling." if req.girlfriend_mode else "That is how imagination becomes entertainment."
        },
        "format_targets": ["video", "podcast", "comic", "novel", "game_concept"]
    }
    return dna

def build_video_script(dna: dict, req: SingularityRequest) -> str:
    if req.girlfriend_mode:
        script = """
        I wanted to make something beautiful just for you.
        It started as a small thought, and then it turned into a quiet little world.
        In that world, the light is soft, the colors are warm, and every second feels gentle.
        It is the kind of place where love does not need to be loud to be real.
        You are the reason it feels alive.
        You are the reason the moments feel sweet.
        You are the reason the whole thing has a heartbeat.
        So this is more than a video.
        It is a small moving memory, made carefully, just to wrap around your heart for a while.
        """
    else:
        script = """
        One idea can become a whole universe.
        First there is a feeling.
        Then a shape.
        Then a story.
        Then something people can actually see and remember.
        This is how imagination stops waiting and starts becoming real.
        """
    return " ".join(line.strip() for line in script.splitlines() if line.strip())

def split_script_into_scenes(script: str):
    parts = [s.strip() for s in re.split(r'(?<=[.!?])\s+', script) if s.strip()]
    return parts[:8] if parts else [script]

def save_story_dna(dna: dict) -> str:
    dna_id = f"{slugify(dna['title'])}_{uuid.uuid4().hex[:6]}"
    path = DNA_DIR / f"{dna_id}.json"
    path.write_text(json.dumps(dna, indent=2, ensure_ascii=False), encoding="utf-8")
    return path.name

def get_fonts():
    try:
        title_font = ImageFont.truetype("arial.ttf", 74)
        body_font = ImageFont.truetype("arial.ttf", 44)
        small_font = ImageFont.truetype("arial.ttf", 34)
    except Exception:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    return title_font, body_font, small_font

def make_background(width: int, height: int, idx: int):
    palette = [
        (18, 14, 28),
        (28, 18, 40),
        (14, 22, 36),
        (32, 20, 30),
        (16, 18, 24),
    ]
    base = palette[idx % len(palette)]
    img = Image.new("RGB", (width, height), color=base)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    for i in range(6):
        alpha = 28 + i * 10
        x0 = 80 + i * 60
        y0 = 160 + i * 140
        x1 = width - (80 + i * 40)
        y1 = height - (220 + i * 110)
        d.rounded_rectangle((x0, y0, x1, y1), radius=90, outline=(255, 255, 255, alpha), width=3)

    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    img = img.filter(ImageFilter.GaussianBlur(radius=0.4))
    return img

def draw_centered_text(draw, box, text, font, fill, spacing=10):
    wrapped = textwrap.fill(text, width=24)
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=spacing, align="center")
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = box[0] + (box[2] - box[0] - tw) / 2
    y = box[1] + (box[3] - box[1] - th) / 2
    draw.multiline_text((x, y), wrapped, font=font, fill=fill, spacing=spacing, align="center")

def make_frame(text: str, title: str, out_path: Path, idx: int, total: int, width: int = 1080, height: int = 1920):
    img = make_background(width, height, idx)
    draw = ImageDraw.Draw(img)
    title_font, body_font, small_font = get_fonts()

    top_box = (80, 110, width - 80, 420)
    main_box = (90, 520, width - 90, 1440)
    bottom_box = (120, 1560, width - 120, 1760)

    draw.rounded_rectangle(main_box, radius=46, fill=(12, 12, 18), outline=(210, 190, 255), width=3)

    draw_centered_text(draw, top_box, title, title_font, (255, 245, 250))
    draw_centered_text(draw, main_box, text, body_font, (232, 236, 245), spacing=16)

    footer = f"{idx + 1}/{total}"
    draw_centered_text(draw, bottom_box, footer, small_font, (210, 210, 225))

    img.save(out_path)

def make_title_card(title: str, out_path: Path, width: int = 1080, height: int = 1920):
    img = Image.new("RGB", (width, height), color=(10, 10, 18))
    draw = ImageDraw.Draw(img)
    title_font, body_font, _ = get_fonts()

    draw_centered_text(draw, (80, 350, width - 80, 850), title, title_font, (255, 240, 248))
    draw_centered_text(draw, (100, 980, width - 100, 1250), "A small moving memory", body_font, (220, 225, 238))
    img.save(out_path)

def make_ending_card(out_path: Path, width: int = 1080, height: int = 1920):
    img = Image.new("RGB", (width, height), color=(14, 12, 20))
    draw = ImageDraw.Draw(img)
    title_font, body_font, _ = get_fonts()

    draw_centered_text(draw, (80, 420, width - 80, 780), "For you, always.", title_font, (255, 242, 246))
    draw_centered_text(draw, (100, 950, width - 100, 1220), "Made with love", body_font, (220, 228, 238))
    img.save(out_path)

def render_video(title: str, script: str, video_slug: str) -> tuple[str, str]:
    audio_path = OUTPUT_DIR / f"{video_slug}.mp3"
    tts = gTTS(text=script, lang="en")
    tts.save(str(audio_path))

    scenes = split_script_into_scenes(script)
    total_scene_count = len(scenes) + 2

    image_paths = []

    title_card = OUTPUT_DIR / f"{video_slug}_title.png"
    make_title_card(title, title_card)
    image_paths.append(title_card)

    for idx, scene in enumerate(scenes, start=1):
        img_path = OUTPUT_DIR / f"{video_slug}_scene_{idx}.png"
        make_frame(scene, title, img_path, idx, total_scene_count)
        image_paths.append(img_path)

    ending_card = OUTPUT_DIR / f"{video_slug}_ending.png"
    make_ending_card(ending_card)
    image_paths.append(ending_card)

    audio_clip = AudioFileClip(str(audio_path))
    total_duration = max(audio_clip.duration, 8)

    title_duration = 2.4
    ending_duration = 2.0
    middle_duration = max(total_duration - title_duration - ending_duration, 4)
    per_middle = middle_duration / max(len(scenes), 1)

    clips = []
    clips.append(ImageClip(str(title_card)).set_duration(title_duration))

    for idx, img_path in enumerate(image_paths[1:-1], start=1):
        clips.append(ImageClip(str(img_path)).set_duration(per_middle))

    clips.append(ImageClip(str(ending_card)).set_duration(ending_duration))

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
            "quality": "upgraded_romantic_video",
            "title": title,
            "story_dna_file": f"/api/singularity/file/{dna_file}",
            "script": script,
            "video_file": f"/api/file/{video_file}",
            "audio_file": f"/api/file/{audio_file}",
            "next_expansions": ["podcast", "comic", "novel", "game_concept"]
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
