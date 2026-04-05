import os
import re
from datetime import datetime, timezone

OUTPUT_DIR = os.path.join("backend", "outputs", "school")

def _slugify(value: str) -> str:
    value = (value or "lesson").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "lesson"

def create_lesson(topic: str, level: str = "beginner", goal: str = "") -> dict:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    now = datetime.now(timezone.utc)
    slug = _slugify(topic)
    filename = f"{slug}_{level}_{int(now.timestamp())}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)

    content = f"""Zerenthis AI School Lesson

Created: {now.isoformat()}
Topic: {topic}
Level: {level}
Goal: {goal}

Lesson Summary:
This lesson gives a structured explanation of {topic} for a {level} learner.

Core Concepts:
1. Definition and framing
2. Why it matters
3. Key moving parts
4. Common mistakes
5. Practical use

Mini Lesson:
- Explain the concept in simple terms
- Show a more advanced framing
- Give one real-world application
- End with a quick recap

Practice:
1. Write the idea in your own words
2. Explain why it matters
3. Apply it to one practical example

Next Step:
Study one adjacent concept and compare the two.
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "status": "completed",
        "module": "school",
        "file_name": filename,
        "file_url": f"/api/file/school/{filename}"
    }
