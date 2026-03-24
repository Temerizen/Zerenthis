from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from moviepy.editor import ColorClip, CompositeVideoClip, concatenate_videoclips
from pathlib import Path
import uuid, threading

app = FastAPI(title="Zerenthis OS")

# ---------------- CONFIG ----------------
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

# ---------------- GENERATION ENGINES ----------------

def video_script(topic):
    return [
        f"Stop scrolling. {topic} is changing everything.",
        f"Most people are already behind.",
        f"This is leverage.",
        f"The gap is growing fast.",
        f"Act now or miss it."
    ]

def short_engine(topic):
    return [
        f"{topic} is about to explode",
        f"Nobody is ready for {topic}",
        f"You are already late to {topic}",
        f"This changes everything about {topic}",
        f"The smartest move right now is {topic}"
    ]

def long_engine(topic):
    return f"""
HOOK:
{topic} is about to change everything.

INTRO:
Most people misunderstand {topic}.

CORE:
This is about leverage, speed, and positioning.

OUTRO:
Act now or fall behind.
"""

def ebook_engine(topic):
    return f"""
TITLE: {topic}

Chapter 1: Introduction
{topic} is evolving rapidly.

Chapter 2: Opportunity
The early advantage matters.

Chapter 3: Execution
Start small, scale fast.

Conclusion:
Take action now.
"""

def pack_engine(topic):
    return {
        "title": f"{topic} Explodes",
        "shorts": short_engine(topic),
        "video_script": video_script(topic),
        "ebook": ebook_engine(topic)
    }

# ---------------- VIDEO RENDER ENGINE ----------------

def render_video(lines):
    uid = str(uuid.uuid4())
    path = OUT / f"{uid}.mp4"

    clips = []

    for i, line in enumerate(lines[:4]):
        bg = ColorClip(
            (720, 1280),
            color=(20 + i*30, 30, 60 + i*20)
        ).set_duration(2)

        # SAFE text overlay alternative (no ImageMagick dependency)
        # we simulate subtitle blocks visually via color variation

        clip = CompositeVideoClip([bg])
        clips.append(clip)

    final = concatenate_videoclips(clips)

    final.write_videofile(
        str(path),
        fps=24,
        codec="libx264",
        audio=False,
        preset="ultrafast",
        verbose=False,
        logger=None
    )

    return path.name

def render_job(job_id, script):
    try:
        video = render_video(script)
        JOBS[job_id] = {
            "status": "done",
            "video_url": f"/files/{video}"
        }
    except Exception as e:
        JOBS[job_id] = {
            "status": "error",
            "error": str(e)
        }

# ---------------- ROUTES ----------------

@app.get("/")
def root():
    return {"status": "Zerenthis Live"}

@app.post("/video")
async def video(req: Request):
    data = await req.json()
    topic = data.get("topic", "AI")

    script = video_script(topic)

    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "processing"}

    threading.Thread(
        target=render_job,
        args=(job_id, script),
        daemon=True
    ).start()

    return {
        "script": script,
        "job_id": job_id
    }

@app.post("/shorts")
async def shorts(req: Request):
    data = await req.json()
    topic = data.get("topic", "AI")
    return {"data": short_engine(topic)}

@app.post("/long")
async def long(req: Request):
    data = await req.json()
    topic = data.get("topic", "AI")
    return {"data": long_engine(topic)}

@app.post("/ebook")
async def ebook(req: Request):
    data = await req.json()
    topic = data.get("topic", "AI")
    return {"data": ebook_engine(topic)}

@app.post("/pack")
async def pack(req: Request):
    data = await req.json()
    topic = data.get("topic", "AI")
    return pack_engine(topic)

@app.post("/banana")
async def banana(req: Request):
    data = await req.json()
    topic = data.get("topic", "AI")

    results = []
    for i in range(5):
        results.append(pack_engine(f"{topic} angle {i}"))

    return {"batch": results}

@app.get("/job/{job_id}")
def job(job_id: str):
    return JOBS.get(job_id, {"status": "not found"})

@app.get("/files/{name}")
def file(name: str):
    path = OUT / name
    if not path.exists():
        return JSONResponse(status_code=404, content={"error": "missing"})
    return FileResponse(path)