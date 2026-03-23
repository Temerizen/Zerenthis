from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from moviepy.editor import *
from gtts import gTTS
from PIL import Image, ImageDraw
import uuid
from pathlib import Path
import random

app = FastAPI(title="Zerenthis GOD Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = Path(__file__).resolve().parent
OUT = BASE / "outputs"
OUT.mkdir(exist_ok=True)

# ----------------------------
# 🧠 VIRAL SCRIPT SYSTEM
# ----------------------------
def generate_script(topic):
    return [
        f"Stop scrolling. {topic} is about to change everything.",
        f"Nobody is talking about this part of {topic}.",
        f"This is where people fall behind.",
        f"This gives you unfair advantage.",
        f"The gap is widening fast.",
        f"If you act now, you win.",
    ]

# ----------------------------
# 🎨 VISUAL STYLE ENGINE
# ----------------------------
def get_color(i):
    styles = [
        (10,12,22),
        (18,14,35),
        (12,22,30),
        (22,16,28),
        (15,15,40),
    ]
    return styles[i % len(styles)]

# ----------------------------
# 🎥 SCENE BUILDER (UPGRADED)
# ----------------------------
def make_scene(text, duration, i):
    bg = ColorClip((1280,720), color=get_color(i)).set_duration(duration)

    zoom = bg.resize(lambda t: 1 + 0.02*t)  # slight zoom effect

    main = TextClip(
        text,
        fontsize=50,
        color="white",
        method="caption",
        size=(1000,500)
    ).set_position("center").set_duration(duration)

    caption = TextClip(
        text.upper(),
        fontsize=32,
        color="cyan",
        method="caption",
        size=(1000,200)
    ).set_position(("center",600)).set_duration(duration)

    return CompositeVideoClip([zoom, main, caption])

# ----------------------------
# 🎬 VIDEO ENGINE (GOD MODE)
# ----------------------------
def build_video(topic):
    uid = str(uuid.uuid4())

    parts = generate_script(topic)
    full_script = " ".join(parts)

    audio_path = OUT / f"{uid}.mp3"
    video_path = OUT / f"{uid}.mp4"

    gTTS(full_script).save(audio_path)

    audio = AudioFileClip(str(audio_path))
    total = audio.duration

    per = total / len(parts)

    clips = []
    for i, p in enumerate(parts):
        clips.append(make_scene(p, per, i))

    final = concatenate_videoclips(clips).set_audio(audio)

    final.write_videofile(str(video_path), fps=24)

    return video_path.name, parts

# ----------------------------
# 🖼 THUMBNAIL ENGINE (UPGRADED)
# ----------------------------
def make_thumbnail(text):
    uid = str(uuid.uuid4())
    path = OUT / f"{uid}.png"

    img = Image.new("RGB", (1280,720), color=(10,12,22))
    draw = ImageDraw.Draw(img)

    draw.text((100,250), text.upper()[:30], fill=(255,255,255))
    draw.text((100,350), "THIS CHANGES EVERYTHING", fill=(0,255,255))

    img.save(path)
    return path.name

# ----------------------------
# ✂️ SHORTS ENGINE
# ----------------------------
def make_shorts(parts):
    return [
        {
            "clip": p,
            "caption": p.upper()
        }
        for p in parts
    ]

# ----------------------------
# 🚀 UNIVERSAL ENDPOINT
# ----------------------------
@app.post("/universal")
async def universal(req: Request):
    data = await req.json()
    prompt = data.get("prompt","AI automation")

    video, parts = build_video(prompt)
    thumb = make_thumbnail(prompt)
    shorts = make_shorts(parts)

    return {
        "type":"god_video",
        "title": f"{prompt} Is About To Explode",
        "video_url": f"/files/{video}",
        "thumbnail_url": f"/files/{thumb}",
        "shorts": shorts,
        "hooks": parts[:2],
        "description": f"This will change how you think about {prompt}. Follow for more.",
        "script": parts
    }

# ----------------------------
# 📦 FILE SERVE
# ----------------------------
@app.get("/files/{filename}")
def get_file(filename: str):
    return FileResponse(OUT / filename)