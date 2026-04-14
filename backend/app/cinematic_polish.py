import random
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip

def smooth_zoom(clip, duration):
    def zoom(t):
        return 1 + 0.06 * (t / duration)
    return clip.resize(zoom)

def cinematic_clip(image_path, duration=3.5):
    clip = ImageClip(image_path).set_duration(duration)
    clip = smooth_zoom(clip, duration)

    # fade in/out
    clip = clip.fadein(0.6).fadeout(0.6)
    return clip

def build_cinematic_sequence(image_paths, audio_path=None):
    clips = []

    for img in image_paths:
        c = cinematic_clip(img, duration=3.5)
        clips.append(c)

    video = concatenate_videoclips(clips, method="compose")

    if audio_path:
        narration = AudioFileClip(audio_path)

        # optional background tone (simple duplication for now)
        audio = CompositeAudioClip([narration])
        video = video.set_audio(audio)

    return video

def enhance_prompt(prompt, girlfriend_mode=False):
    if girlfriend_mode:
        return f"{prompt}, ultra realistic, cinematic lighting, soft glow, depth of field, emotional atmosphere, 8k, volumetric light, romantic color grading"
    else:
        return f"{prompt}, ultra detailed, cinematic lighting, high contrast, 8k, depth of field, film still"

