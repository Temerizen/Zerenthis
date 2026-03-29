import os, uuid
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

OUT_DIR = "backend/data/outputs"
os.makedirs(OUT_DIR, exist_ok=True)

def generate_product(topic):
    styles = getSampleStyleSheet()
    path = os.path.join(OUT_DIR, f"product_{uuid.uuid4()}.pdf")

    doc = SimpleDocTemplate(path)
    content = []

    def p(text):
        content.append(Paragraph(text, styles["Normal"]))
        content.append(Spacer(1,12))

    p(f"<b>{topic} — Premium System</b>")
    p("This is a complete execution system.")

    for i in range(30):
        p(f"Section {i+1}: To succeed in {topic}, focus on execution and consistency.")

    doc.build(content)
    return path
