from pathlib import Path
from backend.core.config import YOUTUBE_DIR, SOCIAL_DIR, PDF_DIR, EMAIL_DIR, THUMBNAIL_DIR
from backend.templates.content_templates import (
    YOUTUBE_SCRIPT_TEMPLATE,
    SOCIAL_POST_TEMPLATE,
    PDF_TEMPLATE,
    EMAIL_TEMPLATE,
    THUMBNAIL_TEMPLATE,
)
from backend.factory.outlines import (
    build_youtube_outline,
    build_social_outline,
    build_pdf_outline,
    build_email_outline,
    build_thumbnail_outline,
)
from backend.factory.run_log import log_content_run, get_recent_content_runs
from backend.utils.files import slugify, timestamp
from backend.utils.writer import write_text_file
from backend.utils.index_builder import rebuild_master_index

def _refresh_index():
    entries = list(reversed(get_recent_content_runs(limit=200)))
    rebuild_master_index(entries)

def generate_youtube_script(topic: str) -> dict:
    data = build_youtube_outline(topic)
    name = f"{timestamp()}_{slugify(topic)}_youtube_script.txt"
    path = Path(YOUTUBE_DIR) / name
    content = YOUTUBE_SCRIPT_TEMPLATE.format(**data)
    output_path = write_text_file(path, content)
    log_content_run("youtube_script", data["title"], topic, output_path)
    _refresh_index()
    return {"content_type": "youtube_script", "title": data["title"], "output_path": output_path}

def generate_social_post(topic: str) -> dict:
    data = build_social_outline(topic)
    name = f"{timestamp()}_{slugify(topic)}_social_post.txt"
    path = Path(SOCIAL_DIR) / name
    content = SOCIAL_POST_TEMPLATE.format(**data)
    output_path = write_text_file(path, content)
    log_content_run("social_post", data["title"], topic, output_path)
    _refresh_index()
    return {"content_type": "social_post", "title": data["title"], "output_path": output_path}

def generate_pdf_brief(topic: str) -> dict:
    data = build_pdf_outline(topic)
    name = f"{timestamp()}_{slugify(topic)}_brief.md"
    path = Path(PDF_DIR) / name
    content = PDF_TEMPLATE.format(**data)
    output_path = write_text_file(path, content)
    log_content_run("pdf_brief", data["title"], topic, output_path)
    _refresh_index()
    return {"content_type": "pdf_brief", "title": data["title"], "output_path": output_path}

def generate_email_draft(topic: str) -> dict:
    data = build_email_outline(topic)
    name = f"{timestamp()}_{slugify(topic)}_email.txt"
    path = Path(EMAIL_DIR) / name
    content = EMAIL_TEMPLATE.format(**data)
    output_path = write_text_file(path, content)
    log_content_run("email_draft", data["title"], topic, output_path)
    _refresh_index()
    return {"content_type": "email_draft", "title": data["title"], "output_path": output_path}

def generate_thumbnail_brief(topic: str) -> dict:
    data = build_thumbnail_outline(topic)
    name = f"{timestamp()}_{slugify(topic)}_thumbnail.txt"
    path = Path(THUMBNAIL_DIR) / name
    content = THUMBNAIL_TEMPLATE.format(**data)
    output_path = write_text_file(path, content)
    log_content_run("thumbnail_brief", data["title"], topic, output_path)
    _refresh_index()
    return {"content_type": "thumbnail_brief", "title": data["title"], "output_path": output_path}

def generate_full_bundle(topic: str) -> dict:
    return {
        "topic": topic,
        "youtube": generate_youtube_script(topic),
        "social": generate_social_post(topic),
        "pdf": generate_pdf_brief(topic),
        "email": generate_email_draft(topic),
        "thumbnail": generate_thumbnail_brief(topic),
    }

def generate_batch(topics: list[str]) -> dict:
    results = []
    for topic in topics:
        clean = (topic or "").strip()
        if clean:
            results.append(generate_full_bundle(clean))
    return {
        "count": len(results),
        "results": results
    }
