from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from moviepy.editor import *
from gtts import gTTS
from PIL import Image, ImageDraw
import uuid
from pathlib import Path

app = FastAPI(title="Zerenthis Viral Engine")

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
# 🧠 VIRAL SCRIPT ENGINE
# ----------------------------
def generate_script(topic):
    return [
        f"Stop scrolling. {topic} is about to change everything.",
        f"Most people completely misunderstand {topic}.",
        f"This is where the real advantage starts.",
        f"If you learn this early, you win faster.",
        f"The gap is getting bigger every day.",
        f"This is your moment to move.",
    ]

# ----------------------------
# 🎥 SCENE CREATOR
# ----------------------------
def make_scene(text, duration, i):
    colors = [
        (10,12,22),
        (18,14,35),
        (12,22,30),
        (22,16,28),
    ]

    bg = ColorClip((1280,720), color=colors[i % len(colors)]).set_duration(duration)

    main = TextClip(
        text,
        fontsize=48,
        color="white",
        method="caption",
        size=(1000,500)
    ).set_position("center").set_duration(duration)

    caption = TextClip(
        text.upper(),
        fontsize=30,
        color="cyan",
        method="caption",
        size=(1000,200)
    ).set_position(("center",600)).set_duration(duration)

    return CompositeVideoClip([bg, main, caption])

# ----------------------------
# 🎬 VIDEO ENGINE
# ----------------------------
def build_video(topic):
    uid = str(uuid.uuid4())

    script_parts = generate_script(topic)
    full_script = " ".join(script_parts)

    audio_path = OUT / f"{uid}.mp3"
    video_path = OUT / f"{uid}.mp4"

    # voice
    gTTS(full_script).save(audio_path)

    audio = AudioFileClip(str(audio_path))
    total = audio.duration

    per = total / len(script_parts)

    clips = []
    for i, part in enumerate(script_parts):
        clips.append(make_scene(part, per, i))

    final = concatenate_videoclips(clips).set_audio(audio)
    final.write_videofile(str(video_path), fps=24)

    return video_path.name, script_parts

# ----------------------------
# 🖼 THUMBNAIL ENGINE
# ----------------------------
def make_thumbnail(text):
    uid = str(uuid.uuid4())
    path = OUT / f"{uid}.png"

    img = Image.new("RGB", (1280,720), color=(10,12,22))
    draw = ImageDraw.Draw(img)

    draw.text((100,300), text[:30].upper(), fill=(255,255,255))

    img.save(path)
    return path.name

# ----------------------------
# ✂️ SHORTS ENGINE
# ----------------------------
def make_shorts(script_parts):
    shorts = []
    for part in script_parts:
        shorts.append({
            "clip": part,
            "caption": part.upper()
        })
    return shorts

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
        "type":"viral_video",
        "title": f"{prompt} Is About To Explode",
        "video_url": f"/files/{video}",
        "thumbnail_url": f"/files/{thumb}",
        "shorts": shorts,
        "description": f"This changes everything about {prompt}. Follow for more.",
        "hooks": parts[:2]
    }

# ----------------------------
# 📦 FILE SERVE
# ----------------------------
@app.get("/files/{filename}")
def get_file(filename: str):
    return FileResponse(OUT / filename)