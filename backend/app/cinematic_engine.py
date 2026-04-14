import random

VOICE_PRESETS = [
    {"tld": "com", "lang": "en"},       # neutral
    {"tld": "co.uk", "lang": "en"},    # softer UK
    {"tld": "com.au", "lang": "en"},   # relaxed AU
    {"tld": "ca", "lang": "en"},       # Canadian tone
]

MUSIC_TRACKS = [
    "soft_piano",
    "ambient_love",
    "cinematic_emotional"
]

def pick_voice():
    return random.choice(VOICE_PRESETS)

def pick_music():
    return random.choice(MUSIC_TRACKS)

def build_scene_prompts(script, girlfriend_mode=False):
    sentences = [s.strip() for s in script.split('.') if s.strip()]
    
    prompts = []
    for s in sentences[:6]:
        if girlfriend_mode:
            prompt = f"romantic cinematic scene, soft lighting, warm tones, dreamy atmosphere, emotional, couple energy, 4k, ultra realistic, {s}"
        else:
            prompt = f"cinematic scene, dramatic lighting, high detail, 4k, {s}"
        prompts.append(prompt)
    
    return prompts

