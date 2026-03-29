import os, uuid
from gtts import gTTS
from moviepy.editor import TextClip, AudioFileClip
from datetime import datetime

OUT_DIR = "backend/data/outputs"
os.makedirs(OUT_DIR, exist_ok=True)

def generate_video(topic):
    script = f"""
If you're struggling with {topic}, listen carefully.

Most people fail because they overcomplicate it.

Step one: keep it simple.
Step two: take action.
Step three: stay consistent.

This is how you win.
"""

    # voice
    audio_path = os.path.join(OUT_DIR, f"{uuid.uuid4()}.mp3")
    gTTS(script).save(audio_path)

    audio = AudioFileClip(audio_path)

    # vertical video
    clip = TextClip(script, fontsize=48, color='white', size=(720,1280), method='caption')
    clip = clip.set_duration(audio.duration).set_audio(audio)

    out_path = os.path.join(OUT_DIR, f"video_{uuid.uuid4()}.mp4")
    clip.write_videofile(out_path, fps=24)

    return out_path
