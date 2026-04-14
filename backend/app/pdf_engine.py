import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

OUTPUT_DIR = "backend/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_pdf(title, content):
    safe_slug = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in (title or "document")).strip("_") or "document"
    file_path = os.path.join(OUTPUT_DIR, f"{safe_slug}.pdf")

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    elements = [
        Paragraph(title or "Generated Document", styles["Title"]),
        Spacer(1, 12),
        Paragraph((content or "").replace("\n", "<br/>"), styles["BodyText"])
    ]

    doc.build(elements)
    return file_path

