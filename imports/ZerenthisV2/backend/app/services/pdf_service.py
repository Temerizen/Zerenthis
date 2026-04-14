def build_pdf_content(title, summary, bullets):
    content = title + "\n\n" + summary + "\n\n"
    content += "\n".join(f"- {b}" for b in bullets)
    return content
