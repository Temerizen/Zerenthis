import os
import uuid
from gtts import gTTS

OUTPUT_DIR = "backend/generated_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_video_package(idea):
    file_id = str(uuid.uuid4())

    script = f"{idea.get('title','')} - {idea.get('promise','')}"

    audio_path = f"{OUTPUT_DIR}/{file_id}.mp3"
    tts = gTTS(script)
    tts.save(audio_path)

    return {
        "script": script,
        "audio": audio_path,
        "status": "phase6_safe_mode"
    }

