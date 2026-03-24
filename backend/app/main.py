from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
from PIL import Image, ImageDraw
from pathlib import Path
import uuid
import threading

app = FastAPI(title="Zerenthis Turbo Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = Path(__file__).resolve().parent
OUT = BASE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

JOBS = {}  # job_id -> status


# ----------------------------
# FAST HELPERS
# ----------------------------
def generate_script(topic: str):
    return [
        f"Stop scrolling. {topic} is about to explode.",
        f"This is what nobody tells you.",
        f"Most people are already behind.",
        f"This gives you leverage.",
        f"The gap is growing fast.",
    ]


def make_thumbnail(text: str):
    uid = str(uuid.uuid4())
    path = OUT / f"{uid}.png"

    img = Image.new("RGB", (1280, 720), color=(10, 12, 22))
    draw = ImageDraw.Draw(img)
    draw.text((90, 250), text[:30].upper(), fill=(255, 255, 255))
    draw.text((90, 350), "WATCH THIS", fill=(0, 255, 255))
    img.save(path)

    return path.name


def make_scene_fast(text: str, duration: float, i: int):
    bg = ColorClip((1280, 720), color=(10, 12, 22)).set_duration(duration)

    txt = TextClip(
        text,
        fontsize=50,
        color="white",
        method="caption",
        size=(1000, 400),
    ).set_position(("center", "center")).set_duration(duration)

    return CompositeVideoClip([bg, txt])


# ----------------------------
# TURBO RENDER (NO AUDIO OPTION)
# ----------------------------
def render_video(job_id, topic, script, fast=True):
    try:
        uid = str(uuid.uuid4())
        video_path = OUT / f"{uid}.mp4"

        lines = script[:3] if fast else script  # fewer scenes = faster
        duration = 2 if fast else 3

        clips = [make_scene_fast(line, duration, i) for i, line in enumerate(lines)]
        final = concatenate_videoclips(clips, method="compose")

        final.write_videofile(
            str(video_path),
            fps=24,
            codec="libx264",
            audio=False,  # 🔥 HUGE SPEED BOOST
            verbose=False,
            logger=None,
        )

        JOBS[job_id]["status"] = "done"
        JOBS[job_id]["video"] = f"/files/{video_path.name}"

    except Exception as e:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)


# ----------------------------
# ROUTES
# ----------------------------
@app.get("/")
def root():
    return {"status": "Turbo Engine Live"}


@app.post("/instant")
async def instant(req: Request):
    data = await req.json()
    topic = data.get("topic", "AI automation")

    script = generate_script(topic)
    thumb = make_thumbnail(topic)

    return {
        "type": "instant",
        "title": f"{topic} Is About To Explode",
        "script": script,
        "thumbnail_url": f"/files/{thumb}",
    }


@app.post("/render-fast")
async def render_fast(req: Request):
    data = await req.json()
    topic = data.get("topic", "AI automation")

    script = generate_script(topic)

    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "processing"}

    threading.Thread(
        target=render_video,
        args=(job_id, topic, script, True),
    ).start()

    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Rendering started (fast mode)",
    }


@app.get("/job/{job_id}")
def job_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return {"error": "job not found"}
    return job


@app.get("/files/{filename}")
def get_file(filename: str):
    file_path = OUT / filename
    if not file_path.exists():
        return JSONResponse(status_code=404, content={"error": "file not found"})
    return FileResponse(file_path)