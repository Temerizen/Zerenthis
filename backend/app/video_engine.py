import os
from gtts import gTTS
from moviepy.editor import TextClip, AudioFileClip, concatenate_videoclips

OUTPUT_DIR = "backend/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_video(topic, script):
    audio_path = os.path.join(OUTPUT_DIR, "voice.mp3")
    video_path = os.path.join(OUTPUT_DIR, "video.mp4")

    tts = gTTS(script)
    tts.save(audio_path)

    audio = AudioFileClip(audio_path)

    clip = TextClip(topic, fontsize=50, size=(1280,720)).set_duration(audio.duration)
    clip = clip.set_audio(audio)

    clip.write_videofile(video_path, fps=24)

    return video_path
