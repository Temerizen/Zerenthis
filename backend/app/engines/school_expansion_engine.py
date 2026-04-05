import os
import re
from datetime import datetime, timezone

OUTPUT_DIR = os.path.join("backend", "outputs", "school")

def _slugify(value: str) -> str:
    value = (value or "course").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "course"

def create_course_pack(topic: str, level: str = "beginner") -> dict:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    now = datetime.now(timezone.utc)
    slug = _slugify(topic)
    bundle = f"{slug}_{level}_{int(now.timestamp())}"
    bundle_dir = os.path.join(OUTPUT_DIR, bundle)
    os.makedirs(bundle_dir, exist_ok=True)

    files = {
        "lesson_1.txt": f"Lesson 1 for {topic}\n\nIntro, framing, and why it matters.\n",
        "lesson_2.txt": f"Lesson 2 for {topic}\n\nCore principles and practical examples.\n",
        "lesson_3.txt": f"Lesson 3 for {topic}\n\nAdvanced view and application.\n",
        "quiz.txt": f"Quiz for {topic}\n\n1. What is it?\n2. Why does it matter?\n3. Give one example.\n",
        "study_sheet.txt": f"Study sheet for {topic}\n\nDefinitions, recap, and review prompts.\n"
    }

    for name, content in files.items():
        with open(os.path.join(bundle_dir, name), "w", encoding="utf-8") as f:
            f.write(content)

    return {
        "status": "completed",
        "module": "school",
        "bundle": bundle,
        "files": [{"file_name": f"{bundle}/{k}", "file_url": f"/api/file/school/{bundle}/{k}"} for k in files.keys()]
    }
