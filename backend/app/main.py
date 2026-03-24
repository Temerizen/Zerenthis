from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
from gtts import gTTS
from PIL import Image, ImageDraw
from pathlib import Path
import uuid

app = FastAPI(title="Zerenthis Stable Engine")

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


def scene_colors():
    return [
        (10, 12, 22),
        (20, 15, 35),
        (12, 22, 30),
        (25, 18, 40),
    ]


def generate_script(topic: str):
    return [
        f"Stop scrolling. {topic} is about to explode.",
        f"This is what nobody tells you about {topic}.",
        f"Most people are already behind.",
        f"This gives you leverage.",
        f"The gap is growing fast.",
        f"Act now or miss it.",
    ]


def make_scene(text: str, duration: float, i: int):
    bg = ColorClip((1280, 720), color=scene_colors()[i % len(scene_colors())]).set_duration(duration)

    main = TextClip(
        text,
        fontsize=46,
        color="white",
        method="caption",
        size=(1000, 420),
        align="center",
    ).set_position(("center", 150)).set_duration(duration)

    caption = TextClip(
        text[:100].upper(),
        fontsize=28,
        color="cyan",
        method="caption",
        size=(1000, 120),
        align="center",
    ).set_position(("center", 590)).set_duration(duration)

    return CompositeVideoClip([bg, main, caption])


def build_video(topic: str):
    uid = str(uuid.uuid4())
    script_parts = generate_script(topic)
    full_script = " ".join(script_parts)

    audio_path = OUT / f"{uid}.mp3"
    video_path = OUT / f"{uid}.mp4"

    gTTS(full_script).save(str(audio_path))
    audio = AudioFileClip(str(audio_path))

    per = max(audio.duration / max(len(script_parts), 1), 1.5)
    clips = [make_scene(part, per, i) for i, part in enumerate(script_parts)]

    final = concatenate_videoclips(clips, method="compose").set_audio(audio)
    final.write_videofile(
        str(video_path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None,
    )

    return video_path.name, script_parts


def make_thumbnail(text: str):
    uid = str(uuid.uuid4())
    path = OUT / f"{uid}.png"

    img = Image.new("RGB", (1280, 720), color=(10, 12, 22))
    draw = ImageDraw.Draw(img)
    draw.text((90, 250), text[:30].upper(), fill=(255, 255, 255))
    draw.text((90, 350), "WATCH THIS", fill=(0, 255, 255))
    img.save(path)

    return path.name


@app.get("/")
def root():
    return {"status": "Zerenthis Stable Engine Live"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/universal")
async def universal(req: Request):
    try:
        data = await req.json()
        prompt = data.get("prompt", "AI automation")

        video_name, script_parts = build_video(prompt)
        thumb_name = make_thumbnail(prompt)

        return {
            "type": "video",
            "title": f"{prompt} Is About To Explode",
            "video_url": f"/files/{video_name}",
            "thumbnail_url": f"/files/{thumb_name}",
            "hooks": script_parts[:2],
            "script": script_parts,
            "description": f"This changes how you think about {prompt}. Follow for more."
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/files/{filename}")
def get_file(filename: str):
    file_path = OUT / filename
    if not file_path.exists():
        return JSONResponse(status_code=404, content={"error": "file not found"})
    return FileResponse(file_path)