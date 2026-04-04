import requests
from pathlib import Path
import uuid

OUTPUT_DIR = Path("backend/data/outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_scene(prompt, idx):
    url = "https://image.pollinations.ai/prompt/" + prompt.replace(" ", "%20")
    file_path = OUTPUT_DIR / f"scene_{idx}_{uuid.uuid4().hex[:6]}.jpg"

    try:
        img = requests.get(url, timeout=30).content
        with open(file_path, "wb") as f:
            f.write(img)
        return str(file_path)
    except:
        return None
