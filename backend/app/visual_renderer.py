import requests
import uuid
import random
from pathlib import Path
from moviepy.editor import ImageClip, concatenate_videoclips
from PIL import Image

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
IMG_DIR = DATA_DIR / "generated_images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

def generate_image(prompt):
    # ⚠️ Replace this with your actual image API later if needed
    url = "https://image.pollinations.ai/prompt/" + prompt.replace(" ", "%20")
    
    filename = f"{uuid.uuid4().hex}.jpg"
    path = IMG_DIR / filename

    try:
        img_data = requests.get(url, timeout=20).content
        with open(path, "wb") as f:
            f.write(img_data)
        return str(path)
    except:
        return None

def cinematic_motion(image_path, duration=3):
    clip = ImageClip(image_path).set_duration(duration)

    # zoom effect
    def zoom(t):
        return 1 + 0.08 * t

    return clip.resize(zoom)

def render_scene_sequence(prompts):
    clips = []

    for prompt in prompts:
        img_path = generate_image(prompt)
        if img_path:
            clip = cinematic_motion(img_path, duration=3)
            clips.append(clip)

    if not clips:
        return None

    return concatenate_videoclips(clips, method="compose")

