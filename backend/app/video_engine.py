import os
import uuid
from gtts import gTTS
from moviepy.editor import TextClip, AudioFileClip, CompositeVideoClip

OUTPUT_DIR = "backend/generated_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# SCRIPT ENGINE
# =========================

def generate_script(idea):
    title = idea.get("title", "Untitled")
    niche = idea.get("niche", "")
    pain = idea.get("pain", "")
    promise = idea.get("promise", "")

    return f"""
Hook: Nobody tells you this about {niche}.

Problem: {pain}

Solution: {promise}

CTA: Link in bio to start.
"""

# =========================
# VOICE GENERATION
# =========================

def generate_voice(script, file_id):
    path = f"{OUTPUT_DIR}/{file_id}_voice.mp3"
    tts = gTTS(script)
    tts.save(path)
    return path

# =========================
# VIDEO GENERATION
# =========================

def generate_video(script, audio_path, file_id):
    video_path = f"{OUTPUT_DIR}/{file_id}.mp4"

    audio = AudioFileClip(audio_path)

    clip = TextClip(
        script,
        fontsize=50,
        size=(720,1280),
        method='caption'
    ).set_duration(audio.duration).set_audio(audio)

    final = CompositeVideoClip([clip])
    final.write_videofile(video_path, fps=24)

    return video_path

# =========================
# THUMBNAIL
# =========================

def generate_thumbnail(title, file_id):
    thumb_path = f"{OUTPUT_DIR}/{file_id}_thumb.png"

    clip = TextClip(
        title,
        fontsize=70,
        size=(720,720),
        method='caption'
    ).set_duration(1)

    clip.save_frame(thumb_path, t=0)
    return thumb_path

# =========================
# MAIN PIPELINE
# =========================

def create_video_package(idea):
    file_id = str(uuid.uuid4())

    script = generate_script(idea)
    audio = generate_voice(script, file_id)
    video = generate_video(script, audio, file_id)
    thumb = generate_thumbnail(idea.get("title",""), file_id)

    return {
        "script": script,
        "video": video,
        "thumbnail": thumb
    }
