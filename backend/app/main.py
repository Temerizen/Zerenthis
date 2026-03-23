from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from gtts import gTTS
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip
import uuid
import os
from pathlib import Path

app = FastAPI(title="Zerenthis Founder Video Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class VideoRequest(BaseModel):
    topic: str = "AI automation"
    title: str | None = None
    script: str | None = None


def build_default_title(topic: str) -> str:
    return f"{topic.title()} Will Change Everything"


def build_default_script(topic: str) -> str:
    return f"""
Most people are underestimating {topic}.

This is not just another trend.
This is a shift in leverage, speed, and opportunity.

The people who understand {topic} early gain an advantage while others wait too long.

If you use {topic} strategically, you can create faster, learn faster, and move with more control.

The real question is not whether {topic} matters.

The real question is whether you will act before everyone else catches on.
""".strip()


def safe_name(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in value.lower())
    return cleaned[:60].strip("-") or str(uuid.uuid4())


def render_video_file(topic: str, title: str, script_text: str) -> dict:
    uid = safe_name(f"{topic}-{uuid.uuid4().hex[:8]}")
    audio_path = OUTPUT_DIR / f"{uid}.mp3"
    video_path = OUTPUT_DIR / f"{uid}.mp4"
    title_path = OUTPUT_DIR / f"{uid}-title.txt"
    desc_path = OUTPUT_DIR / f"{uid}-description.txt"

    # Voice generation
    tts = gTTS(script_text)
    tts.save(str(audio_path))

    audio_clip = AudioFileClip(str(audio_path))
    duration = max(audio_clip.duration, 8)

    # Background
    bg = ColorClip(size=(1280, 720), color=(8, 10, 18)).set_duration(duration)

    # Title text
    title_clip = TextClip(
        title,
        fontsize=56,
        color="white",
        size=(1100, 120),
        method="caption",
        align="center",
    ).set_position(("center", 80)).set_duration(duration)

    # Body text
    body_clip = TextClip(
        script_text[:900],
        fontsize=34,
        color="white",
        size=(1100, 460),
        method="caption",
        align="center",
    ).set_position(("center", 180)).set_duration(duration)

    final = CompositeVideoClip([bg, title_clip, body_clip]).set_audio(audio_clip)
    final.write_videofile(
        str(video_path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None,
    )

    description = (
        f"{title}\n\n"
        f"This video covers {topic}, why it matters, and what people should understand about it.\n\n"
        f"#zerenthis #{safe_name(topic)} #youtube"
    )

    title_path.write_text(title, encoding="utf-8")
    desc_path.write_text(description, encoding="utf-8")

    return {
        "topic": topic,
        "title": title,
        "video_url": f"/files/{video_path.name}",
        "title_url": f"/files/{title_path.name}",
        "description_url": f"/files/{desc_path.name}",
        "filename": video_path.name,
    }


@app.get("/")
def root():
    return {"status": "Zerenthis Founder Video Engine Live"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/generate-video")
def generate_video(topic: str = "AI automation"):
    title = build_default_title(topic)
    script_text = build_default_script(topic)
    return render_video_file(topic, title, script_text)


@app.post("/generate-video")
def generate_video_post(payload: VideoRequest):
    topic = payload.topic
    title = payload.title or build_default_title(topic)
    script_text = payload.script or build_default_script(topic)
    return render_video_file(topic, title, script_text)


@app.get("/files/{filename}")
def get_file(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(file_path), filename=filename)