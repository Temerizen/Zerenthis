import os
import json
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

def _safe_slug(text: str) -> str:
    text = (text or "artifact").strip().lower()
    chars = []
    for ch in text:
        if ch.isalnum():
            chars.append(ch)
        elif ch in [" ", "-", "_"]:
            chars.append("-")
    slug = "".join(chars).strip("-")
    return slug[:60] or "artifact"

def _timestamp():
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")

def _base_filename(title: str):
    return f"{_timestamp()}_{_safe_slug(title)}_{uuid.uuid4().hex[:8]}"

def save_text_artifact(title: str, content: str, ext: str = "md"):
    name = _base_filename(title) + "." + ext
    path = os.path.join(EXPORT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content or "")
    return {"filename": name, "path": path, "format": ext}

def save_json_artifact(title: str, obj):
    name = _base_filename(title) + ".json"
    path = os.path.join(EXPORT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    return {"filename": name, "path": path, "format": "json"}

def save_pdf_artifact(title: str, content: str):
    name = _base_filename(title) + ".pdf"
    path = os.path.join(EXPORT_DIR, name)

    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    x = 50
    y = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, title[:90])
    y -= 24

    c.setFont("Helvetica", 10)
    lines = (content or "").replace("\r\n", "\n").split("\n")
    for raw_line in lines:
        line = raw_line if raw_line else " "
        while len(line) > 95:
            chunk = line[:95]
            c.drawString(x, y, chunk)
            y -= 14
            line = line[95:]
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 50
        c.drawString(x, y, line[:95])
        y -= 14
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 50

    c.save()
    return {"filename": name, "path": path, "format": "pdf"}

def export_bundle(title: str, text: str, obj):
    outputs = []
    outputs.append(save_text_artifact(title, text, "md"))
    outputs.append(save_text_artifact(title, text, "txt"))
    outputs.append(save_json_artifact(title, obj))
    outputs.append(save_pdf_artifact(title, text))
    return outputs

def list_exports():
    items = []
    for name in sorted(os.listdir(EXPORT_DIR), reverse=True):
        path = os.path.join(EXPORT_DIR, name)
        if os.path.isfile(path):
            items.append({
                "filename": name,
                "path": path,
                "size": os.path.getsize(path)
            })
    return items[:200]


