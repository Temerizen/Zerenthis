from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from moviepy.editor import *
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import uuid, os
from pathlib import Path

app = FastAPI(title="Zerenthis Creator Engine")

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
# 🧠 SCRIPT ENGINE (CREATOR STYLE)
# ----------------------------
def generate_script(topic):
    return f"""
[HOOK]
Most people are completely missing what {topic} is really doing.

[BUILD]
This is not just a trend. It is changing leverage, speed, and opportunity.

[INSIGHT]
The people who understand {topic} early are already gaining an advantage.

[PAYOFF]
If you use this correctly, you can move faster than 99% of people.

[CTA]
Follow for more high-leverage insights.
""".strip()

# ----------------------------
# 🎥 VIDEO ENGINE
# ----------------------------
def split_scenes(script):
    return [s.strip() for s in script.split("\n\n") if s.strip()]

def make_scene(text, duration):
    bg = ColorClip((1280,720), color=(10,12,22)).set_duration(duration)

    main = TextClip(
        text,
        fontsize=42,
        color="white",
        method="caption",
        size=(1000,500)
    ).set_position("center").set_duration(duration)

    caption = TextClip(
        text[:100],
        fontsize=28,
        color="cyan",
        method="caption",
        size=(1000,200)
    ).set_position(("center",600)).set_duration(duration)

    return CompositeVideoClip([bg, main, caption])

def build_video(topic, script):
    uid = str(uuid.uuid4())

    audio_path = OUT / f"{uid}.mp3"
    video_path = OUT / f"{uid}.mp4"

    # voice
    gTTS(script).save(audio_path)

    audio = AudioFileClip(str(audio_path))
    duration = audio.duration

    scenes = split_scenes(script)
    per = duration / max(len(scenes),1)

    clips = [make_scene(s, per) for s in scenes]

    final = concatenate_videoclips(clips).set_audio(audio)
    final.write_videofile(str(video_path), fps=24)

    return video_path.name

# ----------------------------
# 🖼 THUMBNAIL ENGINE
# ----------------------------
def make_thumbnail(text):
    uid = str(uuid.uuid4())
    path = OUT / f"{uid}.png"

    img = Image.new("RGB", (1280,720), color=(10,12,22))
    draw = ImageDraw.Draw(img)

    draw.text((100,300), text[:40], fill=(255,255,255))

    img.save(path)
    return path.name

# ----------------------------
# 🚀 UNIVERSAL ROUTE
# ----------------------------
@app.post("/universal")
async def universal(req: Request):
    data = await req.json()
    prompt = data.get("prompt","AI automation")

    script = generate_script(prompt)
    video = build_video(prompt, script)
    thumb = make_thumbnail(prompt)

    return {
        "type":"video",
        "title": f"{prompt} Will Change Everything",
        "video_url": f"/files/{video}",
        "thumbnail_url": f"/files/{thumb}",
        "script": script,
        "description": f"This video explains {prompt}. Subscribe for more."
    }

# ----------------------------
# 📦 FILE SERVE
# ----------------------------
@app.get("/files/{filename}")
def get_file(filename: str):
    return FileResponse(OUT / filename)