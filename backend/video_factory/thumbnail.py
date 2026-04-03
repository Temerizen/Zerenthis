from PIL import Image, ImageDraw

def generate_thumbnail(text):
    img = Image.new("RGB", (1280, 720), color=(0,0,0))
    draw = ImageDraw.Draw(img)
    draw.text((50,300), text[:40], fill=(255,255,255))

    path = "backend/outputs/thumb.jpg"
    img.save(path)

    return path
