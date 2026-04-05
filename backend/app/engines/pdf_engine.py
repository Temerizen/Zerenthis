from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os, time

def create_pdf(product):
    os.makedirs("backend/outputs", exist_ok=True)
    filename = f"backend/outputs/product_{int(time.time())}.pdf"

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph(product["title"], styles["Title"]))
    content.append(Spacer(1, 10))
    content.append(Paragraph(product["summary"], styles["BodyText"]))
    content.append(Spacer(1, 10))

    for step in product["steps"]:
        content.append(Paragraph(f"- {step}", styles["BodyText"]))
        content.append(Spacer(1, 5))

    content.append(Spacer(1, 10))
    content.append(Paragraph(product["monetization"], styles["Italic"]))

    doc.build(content)

    return filename
