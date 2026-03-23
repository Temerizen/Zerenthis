from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from moviepy.editor import *
from gtts import gTTS
import uuid, os
from pathlib import Path

app = FastAPI(title="Zerenthis MAX Engine")

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
# 🧠 ROUTER
# ----------------------------
def detect_type(prompt):
    p = prompt.lower()

    if "video" in p or "youtube" in p:
        return "video"
    if "book" in p:
        return "book"
    if "podcast" in p:
        return "podcast"
    if "music" in p:
        return "music"
    if "game" in p:
        return "game"
    if "app" in p:
        return "app"
    if "anime" in p or "film" in p:
        return "film"

    return "general"

# ----------------------------
# 🎥 CINEMATIC VIDEO ENGINE
# ----------------------------
def split_scenes(script):
    return [s.strip() for s in script.split("\n\n") if s.strip()]

def make_scene(text, duration):
    bg = ColorClip((1280,720), color=(10,12,22)).set_duration(duration)

    txt = TextClip(
        text,
        fontsize=40,
        color="white",
        method="caption",
        size=(1000,500)
    ).set_position("center").set_duration(duration)

    return CompositeVideoClip([bg, txt])

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
# 📚 OTHER ENGINES (STRUCTURED)
# ----------------------------
def book_engine(prompt):
    return {
        "type":"book",
        "title":f"{prompt} Guide",
        "chapters":["Intro","Core","Advanced","Execution"]
    }

def podcast_engine(prompt):
    return {
        "type":"podcast",
        "title":prompt,
        "segments":["intro","main","outro"]
    }

def game_engine(prompt):
    return {
        "type":"game",
        "title":prompt,
        "systems":["combat","progression","inventory"]
    }

# ----------------------------
# 🚀 UNIVERSAL ENDPOINT
# ----------------------------
@app.post("/universal")
async def universal(req: Request):
    data = await req.json()
    prompt = data.get("prompt","AI automation")

    t = detect_type(prompt)

    # VIDEO (REAL OUTPUT)
    if t == "video":
        script = f"""
Most people are underestimating {prompt}.

This changes leverage completely.

Early users gain massive advantage.

The real opportunity is now.
        """.strip()

        video = build_video(prompt, script)

        return {
            "type":"video",
            "title":prompt,
            "video_url":f"/files/{video}",
            "script":script
        }

    if t == "book":
        return book_engine(prompt)

    if t == "podcast":
        return podcast_engine(prompt)

    if t == "game":
        return game_engine(prompt)

    return {
        "type":"general",
        "response":prompt
    }

# ----------------------------
# 📦 FILE SERVE
# ----------------------------
@app.get("/files/{filename}")
def get_file(filename: str):
    path = OUT / filename
    return FileResponse(path)