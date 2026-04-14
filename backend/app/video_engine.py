import os
import textwrap
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip

OUTPUT_DIR = "backend/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def _slugify(value: str) -> str:
    value = (value or "video").strip()
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in value).strip("_") or "video"

def _make_title_image(topic: str, image_path: str):
    width, height = 1280, 720
    bg = (10, 14, 24)
    fg = (255, 255, 255)
    accent = (0, 229, 255)

    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 64)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 28)
    except Exception:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    wrapped = textwrap.wrap(topic or "Generated Video", width=22)
    y = 180

    draw.rounded_rectangle((90, 110, 1190, 610), radius=28, outline=accent, width=4)

    for line in wrapped[:6]:
        bbox = draw.textbbox((0, 0), line, font=font_big)
        text_w = bbox[2] - bbox[0]
        x = (width - text_w) // 2
        draw.text((x, y), line, fill=fg, font=font_big)
        y += 82

    subtitle = "Zerenthis Output Engine"
    bbox = draw.textbbox((0, 0), subtitle, font=font_small)
    sub_w = bbox[2] - bbox[0]
    draw.text(((width - sub_w) // 2, 620), subtitle, fill=accent, font=font_small)

    img.save(image_path)

def create_video(topic, script):
    safe_slug = _slugify(topic)
    image_path = os.path.join(OUTPUT_DIR, f"{safe_slug}.png")
    audio_path = os.path.join(OUTPUT_DIR, f"{safe_slug}_voice.mp3")
    video_path = os.path.join(OUTPUT_DIR, f"{safe_slug}.mp4")

    _make_title_image(topic or "Generated Video", image_path)

    tts = gTTS(script or topic or "Generated video")
    tts.save(audio_path)

    audio = AudioFileClip(audio_path)
    clip = ImageClip(image_path).set_duration(audio.duration).set_audio(audio)

    clip.write_videofile(
        video_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )
    return video_path

def create_video_package(data: dict):
    topic = data.get("topic", "Generated Video")
    script = data.get("script") or data.get("content") or f"Today we are breaking down {topic}."
    video_path = create_video(topic, script)
    return {
        "status": "ok",
        "topic": topic,
        "video": video_path,
        "script": script
    }

