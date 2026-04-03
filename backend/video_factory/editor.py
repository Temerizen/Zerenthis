from moviepy.editor import *

def render_video(script, audio_path, clips):
    video = concatenate_videoclips(clips)
    audio = AudioFileClip(audio_path)
    video = video.set_audio(audio)

    output = "backend/outputs/final_video.mp4"
    video.write_videofile(output, fps=24)

    return output
