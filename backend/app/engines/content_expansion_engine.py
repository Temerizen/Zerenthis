import os
import re
from datetime import datetime, timezone

OUTPUT_DIR = os.path.join("backend", "outputs", "content")

def _slugify(value: str) -> str:
    value = (value or "content_pack").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "content_pack"

def create_campaign_pack(topic: str, platform: str = "multi", angle: str = "growth") -> dict:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    now = datetime.now(timezone.utc)
    slug = _slugify(topic)
    bundle = f"{slug}_{platform}_{int(now.timestamp())}"
    bundle_dir = os.path.join(OUTPUT_DIR, bundle)
    os.makedirs(bundle_dir, exist_ok=True)

    files = {
        "hooks.txt": f"10 hooks for {topic} on {platform}\n\n1. Start here.\n2. This is the angle.\n3. Most people miss this.\n",
        "captions.txt": f"Captions for {topic}\n\n- Useful beats perfect.\n- Publish faster.\n- Learn from response.\n",
        "titles.txt": f"Titles for {topic}\n\n- The Fast Start Blueprint\n- What Actually Works\n- Stop Overcomplicating This\n",
        "calendar.txt": f"7-day calendar for {topic}\n\nDay 1: Hook post\nDay 2: Myth busting\nDay 3: Story post\nDay 4: CTA\n",
        "repurpose_map.txt": f"Repurpose map for {topic}\n\nOne idea -> short video -> thread -> email -> product CTA\n"
    }

    for name, content in files.items():
        with open(os.path.join(bundle_dir, name), "w", encoding="utf-8") as f:
            f.write(content)

    return {
        "status": "completed",
        "module": "content",
        "bundle": bundle,
        "files": [{"file_name": f"{bundle}/{k}", "file_url": f"/api/file/content/{bundle}/{k}"} for k in files.keys()]
    }

