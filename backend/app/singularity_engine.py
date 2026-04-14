from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime, timezone
import json
import textwrap
import re
import uuid
import math
import wave
import struct

from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont, ImageFilter
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
OUTPUT_DIR = DATA_DIR / "outputs"
DNA_DIR = DATA_DIR / "story_dna"
MUSIC_DIR = DATA_DIR / "music_beds"
PODCAST_DIR = DATA_DIR / "podcasts"
COMIC_DIR = DATA_DIR / "comics"
NOVEL_DIR = DATA_DIR / "novels"
GAME_DIR = DATA_DIR / "games"
PACKAGE_DIR = DATA_DIR / "packages"

for p in [OUTPUT_DIR, DNA_DIR, MUSIC_DIR, PODCAST_DIR, COMIC_DIR, NOVEL_DIR, GAME_DIR, PACKAGE_DIR]:
    p.mkdir(parents=True, exist_ok=True)

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

    if req.girlfriend_mode:
        theme = "love, appreciation, tenderness, and emotional safety"
        setting = "a dreamy emotional universe made of memory, warmth, soft light, and little forever moments"
        audio_identity = "soft intimate narration with gentle emotional cadence and emotional underscore"
        protagonist_role = "someone quietly and deeply in love"
        second_role = "the emotional center of the universe"
        hook = "I wanted to make something beautiful just for you."
        middle = "The feeling grows into images, into light, into memories, into a tiny world made to hold affection."
        ending = "So if this feels warm, that is because it was made from real feeling."
    else:
        theme = "transformation, imagination, momentum, and wonder"
        setting = "a cinematic entertainment universe built from imagination and possibility"
        audio_identity = "clean cinematic narration with emotional underscore"
        protagonist_role = "an imaginative creator"
        second_role = "the witness to transformation"
        hook = "One idea can become a whole universe."
        middle = "The idea sharpens into stories, scenes, worlds, systems, and emotion."
        ending = "That is how imagination becomes entertainment."

    return {
        "created_at": now(),
        "idea": req.idea,
        "title": title,
        "audience": req.audience,
        "mode": req.mode,
        "tone": req.tone,
        "visual_style": req.visual_style,
        "girlfriend_mode": req.girlfriend_mode,
        "world": {
            "setting": setting,
            "theme": theme,
            "visual_identity": req.visual_style,
            "audio_identity": audio_identity
        },
        "characters": [
            {
                "name": "Narrator",
                "role": protagonist_role,
                "voice_style": "soft, affectionate, sincere" if req.girlfriend_mode else "clear, warm, cinematic"
            },
            {
                "name": "Beloved" if req.girlfriend_mode else "Audience",
                "role": second_role,
                "voice_style": "silent emotional focal point"
            }
        ],
        "story_arc": {
            "hook": hook,
            "middle": middle,
            "ending": ending
        },
        "format_targets": ["video", "podcast", "comic", "novel", "game_concept", "social_package"]
    }

def build_video_script(dna: dict, req: SingularityRequest) -> str:
    if req.girlfriend_mode and req.mode.lower() == "trailer":
        lines = [
            "I did not just want to say something to you.",
            "I wanted to create something you could feel.",
            "So I built a little world, just for you.",
            "A place where everything feels soft, warm, and real.",
            "Where every moment quietly says you matter.",
            "Because you are the reason it all feels alive.",
            "This is not just a video.",
            "It is something I made for you. Always."
        ]
        return " ".join(lines)

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
        Then something people can actually see, hear, and remember.
        This is how imagination stops waiting and starts becoming real.
        """
    return " ".join(line.strip() for line in script.splitlines() if line.strip())

def build_podcast_script(dna: dict, req: SingularityRequest) -> str:
    title = dna["title"]
    if req.girlfriend_mode:
        text = f"""
        Welcome to {title}.
        This is a little audio letter from one heart to another.
        Sometimes love is not a huge speech. Sometimes it is attention, softness, and choosing someone again and again.
        If I could build a tiny universe for you, it would be full of warmth, safe silence, soft colors, and little details that say you matter.
        It would hold the feeling of being understood without needing to explain everything.
        It would remind you that you are loved in a way that is calm, deep, and real.
        And maybe that is what this is trying to be.
        Not something loud. Just something true.
        A small world, made for you, with tenderness in every corner.
        """
    else:
        text = f"""
        Welcome to {title}.
        This is an idea becoming a world in real time.
        Entertainment begins with a spark, but it grows through structure, feeling, and identity.
        A strong universe creates characters, tone, conflict, memory, and style.
        Once those pieces lock together, one idea can become a video, a podcast, a comic, a novel, or even a game concept.
        That is the power of story DNA.
        """
    return " ".join(line.strip() for line in text.splitlines() if line.strip())

def build_novel_chapter(dna: dict, req: SingularityRequest) -> str:
    title = dna["title"]
    if req.girlfriend_mode:
        chapter = f"""
        Chapter One: {title}

        The first thing he noticed was the light.

        It rested on everything gently, as though the room had decided that harshness was no longer welcome there. It touched the edges of the walls, the quiet corners, the soft places where memory liked to stay. In another life, it might have been an ordinary evening. In this one, it felt like the beginning of a promise.

        He had wanted to make something beautiful for her, though he was not entirely sure when wanting had turned into building. Perhaps it happened the moment he realized that some feelings were too full to remain trapped inside thought. They needed shape. They needed motion. They needed a world.

        So he began there.

        A world with warm colors and patient air. A world where tenderness was not an interruption to reality but the center of it. A world where affection could sit quietly without having to prove itself to anyone.

        And at the center of that world was her.

        Not as a symbol. Not as an idea. But as herself. The reason the small universe had a heartbeat.
        """
    else:
        chapter = f"""
        Chapter One: {title}

        Every universe begins with an unnoticed spark.

        Not a grand explosion. Not a chorus. Just a tiny pressure against the dark, asking to become something more.

        Most ideas die there, suspended between possibility and effort. But some survive. Some gather shape, tone, and conflict. Some begin to attract characters as if personalities were iron filings and the spark was suddenly magnetic.

        That was how this one started.

        It did not know yet whether it wanted to become a film, a comic, a game, or a myth whispered between strangers. It only knew that it wanted to exist.
        """
    return textwrap.dedent(chapter).strip()

def build_comic_outline(dna: dict, req: SingularityRequest) -> dict:
    title = dna["title"]
    if req.girlfriend_mode:
        panels = [
            {"panel": 1, "scene": "Soft title splash with dreamy light and gentle colors", "dialogue": "I wanted to make something beautiful just for you.", "visual_prompt": "romantic cinematic scene, soft glowing light, cinematic, tender atmosphere"},
            {"panel": 2, "scene": "A small universe forming from warm light", "dialogue": "It started as a small thought.", "visual_prompt": "warm emotional cosmic spark becoming a little universe, delicate and beautiful"},
            {"panel": 3, "scene": "The world grows softer and fuller", "dialogue": "Then it became a quiet little world.", "visual_prompt": "gentle fantasy world, warm colors, intimate emotional tone"},
            {"panel": 4, "scene": "Close emotional focus on the beloved as the center", "dialogue": "You are the reason it feels alive.", "visual_prompt": "romantic emotional focal point, cinematic framing, soft expression"},
            {"panel": 5, "scene": "Ending panel with comforting warmth", "dialogue": "A small moving memory, made just to wrap around your heart.", "visual_prompt": "heartwarming final frame, dreamy cinematic romance, gentle glow"}
        ]
    else:
        panels = [
            {"panel": 1, "scene": "A spark in darkness", "dialogue": "One idea can become a whole universe.", "visual_prompt": "cinematic spark in darkness, imagination awakening"},
            {"panel": 2, "scene": "Concept becomes structure", "dialogue": "First there is a feeling. Then a shape.", "visual_prompt": "abstract story world forming, cinematic concept art"},
            {"panel": 3, "scene": "Characters and worlds emerge", "dialogue": "Stories turn into scenes.", "visual_prompt": "stylized entertainment universe, characters, worlds, energy"},
            {"panel": 4, "scene": "The system builds media", "dialogue": "Imagination starts becoming real.", "visual_prompt": "creative studio machine generating media formats"}
        ]
    return {"title": title, "format": "comic_manga_outline", "panels": panels}

def build_game_concept(dna: dict, req: SingularityRequest) -> dict:
    title = dna["title"]
    if req.girlfriend_mode:
        return {
            "title": title,
            "genre": "narrative exploration romance",
            "core_loop": "explore intimate memory spaces, unlock heartfelt scenes, deepen emotional connection",
            "player_goal": "reconstruct a universe made from affection and shared meaning",
            "world_hook": "a dreamlike world where each zone represents a feeling inside a relationship",
            "quests": [
                "Recover scattered memory fragments",
                "Unlock the Warm Light Garden",
                "Restore the Heartbeat Observatory"
            ],
            "systems": [
                "dialogue choices",
                "memory collecting",
                "emotional world restoration"
            ]
        }
    return {
        "title": title,
        "genre": "cinematic narrative adventure",
        "core_loop": "discover lore, unlock scenes, shape the entertainment universe",
        "player_goal": "turn imagination into a living world",
        "world_hook": "a reality where unfinished ideas become places, people, and missions",
        "quests": [
            "Awaken the first world shard",
            "Recruit the story architect",
            "Stabilize the imagination engine"
        ],
        "systems": [
            "dialogue choices",
            "world expansion",
            "story branch unlocking"
        ]
    }

def build_social_package(dna: dict, req: SingularityRequest) -> dict:
    title = dna["title"]
    if req.girlfriend_mode:
        hooks = [
            "I made this little AI love film for my girlfriend.",
            "This started as a thought and turned into a tiny universe.",
            "A soft romantic video made from pure affection."
        ]
        captions = [
            "A small moving memory, made with love.",
            "Sometimes the sweetest things are the quietest.",
            "Made this just to make her smile."
        ]
    else:
        hooks = [
            "One idea turned into a whole entertainment universe.",
            "This is what happens when imagination stops waiting.",
            "AI entertainment studio mode activated."
        ]
        captions = [
            "From spark to story to media.",
            "Building universes from ideas.",
            "Entertainment singularity in motion."
        ]

    return {
        "title": title,
        "hooks": hooks,
        "captions": captions,
        "hashtags": ["#AIStudio", "#StoryWorld", "#Cinematic", "#Shorts", "#CreativeAI"],
        "thumbnail_text": title,
        "cta": "Watch the full piece and follow the universe as it expands."
    }

def split_script_into_scenes(script: str):
    parts = [s.strip() for s in re.split(r'(?<=[.!?])\s+', script) if s.strip()]
    return parts[:8] if parts else [script]

def save_json(folder: Path, title: str, data: dict) -> str:
    file_id = f"{slugify(title)}_{uuid.uuid4().hex[:6]}.json"
    path = folder / file_id
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path.name

def save_text(folder: Path, title: str, suffix: str, content: str) -> str:
    file_id = f"{slugify(title)}_{suffix}_{uuid.uuid4().hex[:6]}.txt"
    path = folder / file_id
    path.write_text(content, encoding="utf-8")
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
    draw_centered_text(draw, bottom_box, f"{idx + 1}/{total}", small_font, (210, 210, 225))

    img.save(out_path)

def make_title_card(title: str, out_path: Path, width: int = 1080, height: int = 1920):
    img = Image.new("RGB", (width, height), color=(10, 10, 18))
    draw = ImageDraw.Draw(img)
    title_font, body_font, _ = get_fonts()
    draw_centered_text(draw, (80, 350, width - 80, 850), title, title_font, (255, 240, 248))
    draw_centered_text(draw, (100, 980, width - 100, 1250), "A small moving memory" if "always" in title.lower() else "A world becoming real", body_font, (220, 225, 238))
    img.save(out_path)

def make_ending_card(out_path: Path, width: int = 1080, height: int = 1920, girlfriend_mode: bool = False):
    img = Image.new("RGB", (width, height), color=(14, 12, 20))
    draw = ImageDraw.Draw(img)
    title_font, body_font, _ = get_fonts()
    line1 = "For you, always." if girlfriend_mode else "The universe continues."
    line2 = "Made with love" if girlfriend_mode else "Created by Zerenthis"
    draw_centered_text(draw, (80, 420, width - 80, 780), line1, title_font, (255, 242, 246))
    draw_centered_text(draw, (100, 950, width - 100, 1220), line2, body_font, (220, 228, 238))
    img.save(out_path)

def smooth_zoom(clip, duration):
    def scale(t):
        return 1.0 + 0.06 * (t / max(duration, 0.001))
    return clip.resize(scale)

def write_music_bed(out_path: Path, duration_seconds: float, girlfriend_mode: bool):
    sample_rate = 44100
    total_frames = int(sample_rate * duration_seconds)
    volume = 0.14 if girlfriend_mode else 0.12

    if girlfriend_mode:
        freqs = [220.0, 329.63, 440.0]
    else:
        freqs = [196.0, 293.66, 392.0]

    with wave.open(str(out_path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(total_frames):
            t = i / sample_rate
            envelope = min(1.0, t / 2.0) * min(1.0, (duration_seconds - t) / 2.0)
            pulse = 0.5 + 0.5 * math.sin(2 * math.pi * 0.2 * t)
            sample = 0.0
            for j, freq in enumerate(freqs):
                sample += math.sin(2 * math.pi * freq * t + j * 0.8)
            sample /= len(freqs)
            sample *= volume * envelope * (0.75 + 0.25 * pulse)
            packed = struct.pack("<h", int(max(-1.0, min(1.0, sample)) * 32767))
            wav_file.writeframesraw(packed)

def render_audio(text: str, slug: str, folder: Path) -> str:
    audio_path = folder / f"{slug}.mp3"
    gTTS(text=text, lang="en").save(str(audio_path))
    return audio_path.name

def get_scene_durations(scene_count: int, total_duration: float, mode: str):
    if scene_count <= 0:
        return []

    if mode.lower() == "trailer" and scene_count >= 4:
        title_d = 1.8
        ending_d = 1.6
        body = max(total_duration - title_d - ending_d, scene_count * 1.4)
        weights = [0.75, 0.85] + [1.0] * max(scene_count - 4, 0) + [1.2, 1.35]
        weights = weights[:scene_count]
        total_w = sum(weights)
        mids = [body * (w / total_w) for w in weights]
        return title_d, mids, ending_d

    title_d = 2.4
    ending_d = 2.0
    body = max(total_duration - title_d - ending_d, 4)
    mids = [body / scene_count] * scene_count
    return title_d, mids, ending_d

def render_video(title: str, script: str, video_slug: str, girlfriend_mode: bool = False, mode: str = "cinematic") -> tuple[str, str, str]:
    narration_path = OUTPUT_DIR / f"{video_slug}.mp3"
    gTTS(text=script, lang="en").save(str(narration_path))

    scenes = split_script_into_scenes(script)

    title_card = OUTPUT_DIR / f"{video_slug}_title.png"
    make_title_card(title, title_card)

    scene_images = []
    for idx, scene in enumerate(scenes, start=1):
        img_path = OUTPUT_DIR / f"{video_slug}_scene_{idx}.png"
        make_frame(scene, title, img_path, idx, len(scenes) + 2)
        scene_images.append(img_path)

    ending_card = OUTPUT_DIR / f"{video_slug}_ending.png"
    make_ending_card(ending_card, girlfriend_mode=girlfriend_mode)

    narration = AudioFileClip(str(narration_path))
    total_duration = max(narration.duration, 10)

    music_path = OUTPUT_DIR / f"{video_slug}_music.wav"
    write_music_bed(music_path, total_duration + 0.5, girlfriend_mode)
    music = AudioFileClip(str(music_path)).volumex(0.18 if girlfriend_mode else 0.15)

    title_d, mids, ending_d = get_scene_durations(len(scene_images), total_duration, mode)

    clips = []
    clips.append(ImageClip(str(title_card)).set_duration(title_d).fadein(0.4).fadeout(0.4))

    for img_path, dur in zip(scene_images, mids):
        clip = ImageClip(str(img_path)).set_duration(dur)
        clip = smooth_zoom(clip, dur).fadein(0.35).fadeout(0.35)
        clips.append(clip)

    clips.append(ImageClip(str(ending_card)).set_duration(ending_d).fadein(0.4).fadeout(0.5))

    video = concatenate_videoclips(clips, method="compose")
    video = video.set_audio(CompositeAudioClip([music, narration]))

    mp4_path = OUTPUT_DIR / f"{video_slug}.mp4"
    video.write_videofile(
        str(mp4_path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )

    narration.close()
    music.close()
    video.close()
    for clip in clips:
        clip.close()

    return mp4_path.name, narration_path.name, music_path.name

@router.post("/api/singularity/create")
def create_singularity(req: SingularityRequest):
    try:
        dna = build_story_dna(req)
        dna_file = save_json(DNA_DIR, dna["title"], dna)

        video_script = build_video_script(dna, req)
        podcast_script = build_podcast_script(dna, req)
        novel_text = build_novel_chapter(dna, req)
        comic_outline = build_comic_outline(dna, req)
        game_concept = build_game_concept(dna, req)
        social_package = build_social_package(dna, req)

        title = dna["title"]
        video_slug = f"{slugify(title)}_{uuid.uuid4().hex[:6]}"

        video_file, audio_file, music_file = render_video(
            title,
            video_script,
            video_slug,
            girlfriend_mode=req.girlfriend_mode,
            mode=req.mode
        )

        podcast_audio = render_audio(podcast_script, f"{video_slug}_podcast", PODCAST_DIR)

        comic_file = save_json(COMIC_DIR, title, comic_outline)
        game_file = save_json(GAME_DIR, title, game_concept)
        social_file = save_json(PACKAGE_DIR, title, social_package)
        novel_file = save_text(NOVEL_DIR, title, "chapter_one", novel_text)
        podcast_script_file = save_text(PODCAST_DIR, title, "script", podcast_script)

        return {
            "ok": True,
            "mode": "multi_format_singularity",
            "quality": "emotional_music_and_beat_sync",
            "title": title,
            "story_dna_file": f"/api/singularity/file/{dna_file}",
            "video": {
                "script": video_script,
                "video_file": f"/api/file/{video_file}",
                "audio_file": f"/api/file/{audio_file}",
                "music_file": f"/api/file/{music_file}"
            },
            "podcast": {
                "script_file": f"/api/podcast/file/{podcast_script_file}",
                "audio_file": f"/api/podcast/file/{podcast_audio}"
            },
            "comic": {
                "outline_file": f"/api/comic/file/{comic_file}"
            },
            "novel": {
                "chapter_file": f"/api/novel/file/{novel_file}"
            },
            "game_concept": {
                "concept_file": f"/api/game/file/{game_file}"
            },
            "social_package": {
                "package_file": f"/api/package/file/{social_file}"
            }
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

@router.get("/api/podcast/file/{name:path}")
def get_podcast_file(name: str):
    safe_name = Path(name).name
    target = PODCAST_DIR / safe_name
    if target.exists() and target.is_file():
        return FileResponse(str(target), filename=safe_name)
    raise HTTPException(status_code=404, detail="podcast file not found")

@router.get("/api/comic/file/{name:path}")
def get_comic_file(name: str):
    safe_name = Path(name).name
    target = COMIC_DIR / safe_name
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="comic file not found")
    return FileResponse(str(target), filename=safe_name)

@router.get("/api/novel/file/{name:path}")
def get_novel_file(name: str):
    safe_name = Path(name).name
    target = NOVEL_DIR / safe_name
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="novel file not found")
    return FileResponse(str(target), filename=safe_name)

@router.get("/api/game/file/{name:path}")
def get_game_file(name: str):
    safe_name = Path(name).name
    target = GAME_DIR / safe_name
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="game concept file not found")
    return FileResponse(str(target), filename=safe_name)

@router.get("/api/package/file/{name:path}")
def get_package_file(name: str):
    safe_name = Path(name).name
    target = PACKAGE_DIR / safe_name
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="package file not found")
    return FileResponse(str(target), filename=safe_name)


