from .script_gen import generate_script
from .voice_gen import generate_voice
from .visuals import get_visuals
from .editor import render_video
from .thumbnail import generate_thumbnail

def run_video_factory(topic, style="tiktok"):
    script = generate_script(topic, style)
    audio_path = generate_voice(script)
    clips = get_visuals(script)
    video_path = render_video(script, audio_path, clips)
    thumb_path = generate_thumbnail(topic)

    return {
        "video": video_path,
        "thumbnail": thumb_path,
        "script": script
    }
