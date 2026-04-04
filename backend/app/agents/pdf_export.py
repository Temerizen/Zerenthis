# tools/pdf_export.py

from fpdf import FPDF
import os

def save_pdf(title, content, folder="reports"):
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, title.replace(" ", "_") + ".pdf")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in content.split("\n"):
        pdf.multi_cell(0, 5, line)

    pdf.output(filename)
    print(f"[PDF saved] {filename}")