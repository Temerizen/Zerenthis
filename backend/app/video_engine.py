import os
from gtts import gTTS
from moviepy.editor import TextClip, AudioFileClip

OUTPUT_DIR = "backend/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_video(topic, script):
    safe_slug = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in (topic or "video")).strip("_") or "video"
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
