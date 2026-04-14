from PIL import Image, ImageDraw, ImageFont
import os

def _font(size=72):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/Arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf"
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                pass
    return ImageFont.load_default()

def generate_thumbnail(text: str, output_path: str, title: str = ""):
    img = Image.new("RGB", (1280, 720), (18, 18, 24))
    draw = ImageDraw.Draw(img)

    # background blocks
    draw.rectangle((0, 0, 1280, 720), fill=(18, 18, 24))
    draw.rectangle((60, 60, 1220, 660), outline=(255, 210, 60), width=6)
    draw.rectangle((80, 420, 1200, 620), fill=(30, 30, 40))

    font_big = _font(96)
    font_med = _font(42)

    text = (text or "WATCH THIS").strip().upper()
    title = (title or "").strip()

    draw.text((100, 110), "SEMANTIQAI", font=font_med, fill=(255, 210, 60))
    draw.text((100, 470), text[:28], font=font_big, fill=(255, 255, 255))

    if title:
        draw.text((100, 230), title[:60], font=font_med, fill=(180, 180, 180))

    img.save(output_path)
    return output_path
