from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

def _font(size=54):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/Arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf"
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                pass
    return ImageFont.load_default()

def render_scene_card(scene: dict, output_path: str, title: str = ""):
    img = Image.new("RGB", (1920, 1080), (10, 10, 14))
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, 0, 1920, 1080), fill=(10, 10, 14))
    draw.rectangle((70, 70, 1850, 1010), outline=(255, 210, 60), width=4)

    font_title = _font(72)
    font_sub = _font(40)
    font_body = _font(46)

    scene_title = (scene.get("headline") or "Scene").strip()
    visual_prompt = (scene.get("visual_prompt") or "").strip()
    onscreen = (scene.get("onscreen_text") or "").strip()

    draw.text((120, 110), title[:55], font=font_sub, fill=(255, 210, 60))
    draw.text((120, 220), scene_title[:40], font=font_title, fill=(255, 255, 255))

    wrapped_visual = textwrap.fill(visual_prompt[:220], width=36)
    draw.text((120, 360), wrapped_visual, font=font_body, fill=(170, 170, 190))

    draw.rectangle((120, 820, 1800, 940), fill=(26, 26, 34))
    draw.text((160, 845), onscreen[:60].upper(), font=font_body, fill=(255, 255, 255))

    img.save(output_path)
    return output_path
