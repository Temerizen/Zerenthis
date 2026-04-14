import os
import re
from datetime import datetime, timezone

OUTPUT_DIR = os.path.join("backend", "outputs", "cognitive")

def _slugify(value: str) -> str:
    value = (value or "cognitive_pack").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "cognitive_pack"

def create_training_pack(focus: str, level: str = "medium") -> dict:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    now = datetime.now(timezone.utc)
    slug = _slugify(focus)
    bundle = f"{slug}_{level}_{int(now.timestamp())}"
    bundle_dir = os.path.join(OUTPUT_DIR, bundle)
    os.makedirs(bundle_dir, exist_ok=True)

    files = {
        "memory_drill.txt": f"Memory drill for {focus}\n\nRecall, restate, rebuild.\n",
        "reasoning_drill.txt": f"Reasoning drill for {focus}\n\nBreak down an argument and rebuild it.\n",
        "abstraction_drill.txt": f"Abstraction drill for {focus}\n\nMove between simple and advanced framing.\n",
        "reflection.txt": f"Reflection prompts for {focus}\n\nWhat was hard? What became clearer?\n",
        "progress_sheet.txt": f"Progress sheet for {focus}\n\nTrack difficulty, recall, and clarity.\n"
    }

    for name, content in files.items():
        with open(os.path.join(bundle_dir, name), "w", encoding="utf-8") as f:
            f.write(content)

    return {
        "status": "completed",
        "module": "cognitive",
        "bundle": bundle,
        "files": [{"file_name": f"{bundle}/{k}", "file_url": f"/api/file/cognitive/{bundle}/{k}"} for k in files.keys()]
    }

