from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os

OUTPUT_DIR = "backend/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_pdf(title, content):
    file_path = os.path.join(OUTPUT_DIR, "document.pdf")
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Paragraph(content, styles["BodyText"]))

    doc.build(elements)
    return file_path
