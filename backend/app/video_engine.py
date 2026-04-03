import os
from gtts import gTTS
from moviepy.editor import TextClip, AudioFileClip

OUTPUT_DIR = "backend/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def _slugify(value: str) -> str:
    value = (value or "video").strip()
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in value).strip("_") or "video"

def create_video(topic, script):
    safe_slug = _slugify(topic)
    audio_path = os.path.join(OUTPUT_DIR, f"{safe_slug}_voice.mp3")
    video_path = os.path.join(OUTPUT_DIR, f"{safe_slug}.mp4")

    tts = gTTS(script or topic or "Generated video")
    tts.save(audio_path)

    audio = AudioFileClip(audio_path)
    clip = TextClip(
        txt=topic or "Generated Video",
        fontsize=50,
        size=(1280, 720),
        color="white",
        method="caption"
    ).set_duration(audio.duration).set_audio(audio)

    clip.write_videofile(video_path, fps=24)
    return video_path

def create_video_package(data: dict):
    topic = data.get("topic", "Generated Video")
    script = data.get("script") or data.get("content") or f"Today we are breaking down {topic}."
    video_path = create_video(topic, script)
    return {
        "status": "ok",
        "topic": topic,
        "video": video_path,
        "script": script
    }
