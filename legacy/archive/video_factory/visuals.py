from moviepy.editor import ColorClip

def get_visuals(script):
    clips = []
    for i in range(5):
        clip = ColorClip(size=(1080,1920), color=(0,0,0), duration=3)
        clips.append(clip)
    return clips
