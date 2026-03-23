from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from moviepy.editor import *
from gtts import gTTS
from PIL import Image, ImageDraw
import uuid, random
from pathlib import Path

app = FastAPI(title="Zerenthis Autonomous Factory")

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
# 🧠 VIRAL IDEA VARIATIONS
# ----------------------------
def expand_topics(topic):
    angles = [
        "The hidden truth about",
        "Why nobody talks about",
        "The real power of",
        "What most people miss about",
        "The future of",
        "How this changes everything:",
    ]
    return [f"{a} {topic}" for a in angles]

# ----------------------------
# 🧠 SCRIPT ENGINE
# ----------------------------
def generate_script(topic):
    return [
        f"Stop scrolling. {topic} is about to explode.",
        f"This is what nobody tells you about {topic}.",
        f"Most people are already behind.",
        f"This gives you leverage.",
        f"The gap is growing fast.",
        f"Act now or miss it."
    ]

# ----------------------------
# 🎥 SCENE
# ----------------------------
def make_scene(text, duration, i):
    colors = [(10,12,22),(20,15,35),(12,22,30),(25,18,40)]

    bg = ColorClip((1280,720), color=colors[i % len(colors)]).set_duration(duration)

    zoom = bg.resize(lambda t: 1 + 0.02*t)

    main = TextClip(text, fontsize=48, color="white",
                    method="caption", size=(1000,500)
                    ).set_position("center").set_duration(duration)

    return CompositeVideoClip([zoom, main])

# ----------------------------
# 🎬 VIDEO ENGINE
# ----------------------------
def build_video(topic):
    uid = str(uuid.uuid4())

    parts = generate_script(topic)
    full = " ".join(parts)

    audio_path = OUT / f"{uid}.mp3"
    video_path = OUT / f"{uid}.mp4"

    gTTS(full).save(audio_path)

    audio = AudioFileClip(str(audio_path))
    per = audio.duration / len(parts)

    clips = [make_scene(p, per, i) for i,p in enumerate(parts)]

    final = concatenate_videoclips(clips).set_audio(audio)
    final.write_videofile(str(video_path), fps=24)

    return video_path.name, parts

# ----------------------------
# 🖼 THUMBNAIL
# ----------------------------
def make_thumbnail(text):
    uid = str(uuid.uuid4())
    path = OUT / f"{uid}.png"

    img = Image.new("RGB", (1280,720), color=(10,12,22))
    draw = ImageDraw.Draw(img)

    draw.text((100,250), text[:30].upper(), fill=(255,255,255))
    draw.text((100,350), "WATCH THIS", fill=(0,255,255))

    img.save(path)
    return path.name

# ----------------------------
# 🏭 FACTORY ENGINE
# ----------------------------
def generate_batch(topic, count=5):
    topics = expand_topics(topic)

    batch = []

    for i in range(min(count, len(topics))):
        t = topics[i]

        video, parts = build_video(t)
        thumb = make_thumbnail(t)

        batch.append({
            "title": t,
            "video_url": f"/files/{video}",
            "thumbnail_url": f"/files/{thumb}",
            "hooks": parts[:2],
            "script": parts
        })

    return batch

# ----------------------------
# 🚀 FACTORY ROUTE
# ----------------------------
@app.post("/factory")
async def factory(req: Request):
    data = await req.json()

    topic = data.get("topic", "AI automation")
    count = int(data.get("count", 5))

    batch = generate_batch(topic, count)

    return {
        "type":"factory_batch",
        "total": len(batch),
        "items": batch
    }

# ----------------------------
# 📦 FILE SERVER
# ----------------------------
@app.get("/files/{filename}")
def get_file(filename: str):
    return FileResponse(OUT / filename)