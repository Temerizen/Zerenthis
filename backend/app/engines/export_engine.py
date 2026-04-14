from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

def _wrap_lines(text: str, string_width, font_name: str, font_size: int, max_width: float) -> list[str]:
    words = (text or "").split()
    if not words:
        return [""]
    lines = []
    current = words[0]
    for word in words[1:]:
        trial = current + " " + word
        if string_width(trial, font_name, font_size) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines

def _draw_block(c, text: str, x: int, y: int, max_width: int, string_width, font_name: str = "Helvetica", font_size: int = 11, leading: int = 15) -> int:
    c.setFont(font_name, font_size)
    for raw_line in (text or "").splitlines():
        wrapped = _wrap_lines(raw_line, string_width, font_name, font_size, max_width) if raw_line.strip() else [""]
        for line in wrapped:
            c.drawString(x, y, line)
            y -= leading
    return y

def export_product_pdf(bundle: Dict[str, Any], output_path: str) -> str:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfgen import canvas

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    product = bundle.get("product", {}) or {}
    offer = bundle.get("offer", {}) or {}
    traffic = bundle.get("traffic", {}) or {}

    title = str(product.get("title", "Premium Digital System")).strip()
    description = str(product.get("description", "")).strip()
    steps = product.get("steps", []) or []
    value_bullets = product.get("value_bullets", []) or []
    bonus = str(product.get("bonus", "")).strip()
    price = str(offer.get("price_suggestion", "29")).strip()
    urgency = str(offer.get("urgency_angle", "")).strip()
    hooks = traffic.get("hooks", []) or []
    captions = traffic.get("captions", []) or []

    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    x = 50
    y = height - 50
    max_width = 500

    c.setTitle(title)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(x, y, title)
    y -= 28

    c.setFont("Helvetica", 11)
    c.drawString(x, y, f"Suggested Price: ${price}")
    y -= 24

    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "Description")
    y -= 18
    y = _draw_block(c, description, x, y, max_width, stringWidth)

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "System Steps")
    y -= 18
    for i, step in enumerate(steps, start=1):
        y = _draw_block(c, f"{i}. {step}", x, y, max_width, stringWidth)
        if y < 90:
            c.showPage()
            y = height - 50

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "Value Bullets")
    y -= 18
    for bullet in value_bullets:
        y = _draw_block(c, f"- {bullet}", x, y, max_width, stringWidth)
        if y < 90:
            c.showPage()
            y = height - 50

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "Bonus")
    y -= 18
    y = _draw_block(c, bonus, x, y, max_width, stringWidth)

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "Urgency Angle")
    y -= 18
    y = _draw_block(c, urgency, x, y, max_width, stringWidth)

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "Hooks")
    y -= 18
    for hook in hooks:
        y = _draw_block(c, f"- {hook}", x, y, max_width, stringWidth)
        if y < 90:
            c.showPage()
            y = height - 50

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "Captions")
    y -= 18
    for caption in captions:
        y = _draw_block(c, f"- {caption}", x, y, max_width, stringWidth)
        if y < 90:
            c.showPage()
            y = height - 50

    c.save()
    return str(path)

