from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uuid, threading, textwrap
from moviepy.editor import ColorClip, concatenate_videoclips, AudioClip
import numpy as np

app = FastAPI(title="Zerenthis GOD CORE")

BASE = Path(__file__).resolve().parent
OUT = BASE / "outputs"
OUT.mkdir(exist_ok=True)

JOBS = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- CONTENT ENGINE ----------------

def generate_script(topic):
    return [
        f"Stop scrolling. {topic} is changing everything.",
        f"Most people are already behind.",
        f"This is leverage.",
        f"The gap is growing fast.",
        f"Act now or miss it."
    ]

def generate_shorts(topic):
    return [
        f"{topic} is about to explode",
        f"You are already behind in {topic}",
        f"Nobody is ready for {topic}"
    ]

def generate_long(topic):
    return f"{topic} is the next shift. Learn fast or fall behind."

def generate_ebook(topic):
    return f"{topic}\n\nMini book about {topic}"

def generate_pack(topic):
    return {
        "title": f"{topic} Explodes",
        "script": generate_script(topic),
        "shorts": generate_shorts(topic),
        "ebook": generate_ebook(topic)
    }

# ---------------- INTELLIGENCE ----------------

def ai_brain(topic):
    return {
        "analysis": f"{topic} creates leverage through speed.",
        "insight": "Early movers dominate.",
        "conclusion": "Act now."
    }

def research(topic):
    return {
        "trend": "growing",
        "opportunity": "high",
        "summary": f"{topic} is rising fast"
    }

def execution_plan(topic):
    return [
        f"Pick niche in {topic}",
        "Create content daily",
        "Track performance",
        "Scale winners"
    ]

def monetization(topic):
    return [
        "affiliate links",
        "digital products",
        "ads",
        "services"
    ]

# ---------------- VIDEO ENGINE ----------------

def make_audio(duration):
    def frame(t): return 0.2*np.sin(440*2*np.pi*t)
    return AudioClip(frame, duration=duration, fps=44100)

def render_video(lines):
    uid = str(uuid.uuid4())
    path = OUT / f"{uid}.mp4"

    clips = []
    for i in range(4):
        clip = ColorClip((720,1280), color=(20+i*20,30,60+i*20)).set_duration(2)
        clips.append(clip)

    video = concatenate_videoclips(clips)
    audio = make_audio(video.duration)
    video = video.set_audio(audio)

    video.write_videofile(
        str(path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        verbose=False,
        logger=None
    )

    return path.name

def render_job(job_id, script):
    try:
        vid = render_video(script)
        JOBS[job_id] = {"status":"done","video_url":f"/files/{vid}"}
    except Exception as e:
        JOBS[job_id] = {"status":"error","error":str(e)}

# ---------------- BANANA MODE (FULL SYSTEM) ----------------

def banana_system(topic):
    batch = []

    for i in range(5):
        angle = f"{topic} angle {i}"

        entry = {
            "content": generate_pack(angle),
            "brain": ai_brain(angle),
            "research": research(angle),
            "execution": execution_plan(angle),
            "monetization": monetization(angle),
            "score": len(angle) % 10 + 5
        }

        batch.append(entry)

    best = max(batch, key=lambda x: x["score"])

    return {
        "batch": batch,
        "best": best
    }

# ---------------- ROUTES ----------------

@app.get("/")
def root():
    return {"status":"Zerenthis GOD CORE Live"}

@app.post("/video")
async def video(req: Request):
    data = await req.json()
    topic = data.get("topic","AI")

    script = generate_script(topic)

    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status":"processing"}

    threading.Thread(target=render_job,args=(job_id,script),daemon=True).start()

    return {"script":script,"job_id":job_id}

@app.post("/shorts")
async def shorts(req: Request):
    data = await req.json()
    return {"data":generate_shorts(data.get("topic","AI"))}

@app.post("/long")
async def long(req: Request):
    data = await req.json()
    return {"data":generate_long(data.get("topic","AI"))}

@app.post("/ebook")
async def ebook(req: Request):
    data = await req.json()
    return {"data":generate_ebook(data.get("topic","AI"))}

@app.post("/pack")
async def pack(req: Request):
    data = await req.json()
    return generate_pack(data.get("topic","AI"))

@app.post("/banana")
async def banana(req: Request):
    data = await req.json()
    return banana_system(data.get("topic","AI"))

@app.get("/job/{id}")
def job(id:str):
    return JOBS.get(id,{"status":"not found"})

@app.get("/files/{name}")
def file(name:str):
    path = OUT / name
    if not path.exists():
        return JSONResponse(status_code=404, content={"error":"missing"})
    return FileResponse(path)