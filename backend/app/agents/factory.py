from .content_brain import generate_video_script
from .thumbnail_engine import generate_thumbnail_prompt

def generate_batch(topics):
    results = []

    for topic in topics:
        script = generate_video_script(topic)
        thumb = generate_thumbnail_prompt(topic)

        results.append({
            "topic": topic,
            "script": script,
            "thumbnail": thumb
        })

    return results

