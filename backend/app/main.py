from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from moviepy.editor import ColorClip, concatenate_videoclips
from pathlib import Path
import uuid, threading

app = FastAPI(title="Zerenthis OS")

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

JOBS = {}

# ------------------ GENERATORS ------------------

def generate_video_script(topic):
    return [
        f"Stop scrolling. {topic} is changing everything.",
        f"Most people are already behind.",
        f"This is leverage.",
        f"The gap is growing fast.",
        f"Act now or miss it."
    ]

def generate_short_batch(topic):
    return [
        f"{topic} is about to explode",
        f"Nobody is ready for {topic}",
        f"This changes everything about {topic}"
    ]

def generate_long_script(topic):
    return f"""
HOOK:
{topic} is about to shift everything.

INTRO:
Most people misunderstand {topic}.

CORE:
This is about leverage, speed, and positioning.

OUTRO:
The gap is growing. Decide now.
"""

def generate_ebook(topic):
    return f"""
TITLE: {topic}

Chapter 1:
Introduction to {topic}

Chapter 2:
Why it matters

Chapter 3:
How to use it

Conclusion:
Take action.
"""

def generate_content_pack(topic):
    return {
        "title": f"{topic} Explodes",
        "shorts": generate_short_batch(topic),
        "script": generate_video_script(topic),
        "ebook": generate_ebook(topic)
    }

# ------------------ VIDEO ------------------

def render_video(lines):
    uid = str(uuid.uuid4())
    path = OUT / f"{uid}.mp4"

    clips = []
    for i in range(3):
        clip = ColorClip((720,1280), color=(10+i*30,20,40)).set_duration(2)
        clips.append(clip)

    final = concatenate_videoclips(clips)

    final.write_videofile(
        str(path),
        fps=12,
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
        JOBS[job_id] = {"status":"done","video_url":f"/files/{video}"}
    except Exception as e:
        JOBS[job_id] = {"status":"error","error":str(e)}

# ------------------ ROUTES ------------------

@app.get("/")
def root():
    return {"status":"Zerenthis OS Live"}

@app.post("/video")
async def video(req: Request):
    data = await req.json()
    topic = data.get("topic","AI")

    script = generate_video_script(topic)

    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status":"processing"}

    threading.Thread(target=render_job,args=(job_id,script),daemon=True).start()

    return {"script":script,"job_id":job_id}

@app.post("/shorts")
async def shorts(req: Request):
    data = await req.json()
    return {"data":generate_short_batch(data.get("topic","AI"))}

@app.post("/long")
async def long(req: Request):
    data = await req.json()
    return {"data":generate_long_script(data.get("topic","AI"))}

@app.post("/ebook")
async def ebook(req: Request):
    data = await req.json()
    return {"data":generate_ebook(data.get("topic","AI"))}

@app.post("/pack")
async def pack(req: Request):
    data = await req.json()
    return generate_content_pack(data.get("topic","AI"))

@app.post("/banana")
async def banana(req: Request):
    data = await req.json()
    topic = data.get("topic","AI")

    results = []
    for i in range(5):
        results.append(generate_content_pack(f"{topic} angle {i}"))

    return {"batch":results}

@app.get("/job/{id}")
def job(id:str):
    return JOBS.get(id,{"status":"not found"})

@app.get("/files/{name}")
def file(name:str):
    path = OUT / name
    if not path.exists():
        return JSONResponse(status_code=404, content={"error":"missing"})
    return FileResponse(path)