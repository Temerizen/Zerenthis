# test_paper.py
from generate_content import generate_academic_paper, export_pdf

# Preloaded legal datasets
datasets = [
    ("https://datahub.io/core/country-list/r/data.csv", "csv", "Country List"),
    ("https://datahub.io/core/gdp/r/gdp.csv", "csv", "World GDP"),
    ("https://datahub.io/core/population/r/population.csv", "csv", "World Population"),
]

# Generate paper on test topic
topic = "Artificial Intelligence in Healthcare"
paper_sections, figures = generate_academic_paper(topic, max_results=5, datasets=datasets)

# Save TXT
txt_file = topic.replace(" ", "_") + "_Legal_Academic_Paper.txt"
with open(txt_file, "w", encoding="utf-8") as f:
    f.write(f"# {topic}\n\n")
    for sec, text in paper_sections.items():
        f.write(f"## {sec}\n{text}\n\n")

# Save PDF
pdf_file = topic.replace(" ", "_") + "_Legal_Academic_Paper.pdf"
export_pdf(pdf_file, topic, paper_sections, figures)

print(f"[Success] Generated files:\nTXT: {txt_file}\nPDF: {pdf_file}")
