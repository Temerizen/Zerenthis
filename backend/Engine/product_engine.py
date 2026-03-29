from __future__ import annotations

import os
import re
import uuid
from pathlib import Path
from typing import List

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "data" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value or "zerenthis-output"


def _title_case(text: str) -> str:
    return " ".join(word.capitalize() for word in text.split())


def _build_title(topic: str, promise: str) -> str:
    promise = (promise or "").strip()
    if promise:
        return f"{_title_case(topic)} System for {promise}"
    return f"{_title_case(topic)} Premium System"


def _make_sales_bullets(topic: str, buyer: str, promise: str) -> List[str]:
    return [
        f"A clear path for {buyer.lower()} who want to {promise or f'move faster with {topic}'}",
        "Structured sections that feel premium instead of messy",
        "Actionable prompts, templates, and checklists",
        "Fast-start guidance for someone who needs movement now",
        "A product body designed to feel useful, not generic",
    ]


def build_product_pack(
    *,
    topic: str,
    niche: str,
    tone: str,
    buyer: str,
    promise: str,
    bonus: str,
    notes: str,
    base_url: str,
) -> dict:
    title = _build_title(topic, promise)
    slug = _slugify(title)
    filename = f"{slug}-{uuid.uuid4().hex[:8]}.pdf"
    path = OUTPUT_DIR / filename

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        spaceAfter=10,
    )
    bullet_style = ParagraphStyle(
        "Bulletish",
        parent=body_style,
        leftIndent=12,
        bulletIndent=0,
        spaceBefore=2,
        spaceAfter=6,
    )

    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=0.72 * inch,
        rightMargin=0.72 * inch,
        topMargin=0.8 * inch,
        bottomMargin=0.8 * inch,
        title=title,
        author="Zerenthis",
    )

    story = []

    def add_heading(text: str) -> None:
        story.append(Paragraph(text, heading_style))
        story.append(Spacer(1, 8))

    def add_body(text: str) -> None:
        story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 6))

    def add_bullets(items: List[str]) -> None:
        for item in items:
            story.append(Paragraph(f"• {item}", bullet_style))
        story.append(Spacer(1, 8))

    sales_bullets = _make_sales_bullets(topic, buyer, promise)
    subtitle = (
        f"A premium {niche.lower()} guide in a {tone.lower()} tone for {buyer.lower()}."
    )

    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph(subtitle, body_style))
    story.append(Spacer(1, 16))

    add_heading("What This Product Is")
    add_body(
        f"This guide is built for people who want a cleaner, stronger path into {topic}. "
        f"Instead of drowning the reader in vague advice, it packages a practical system with a premium feel."
    )

    add_heading("Who This Is For")
    add_body(
        f"This is for {buyer.lower()} in the {niche.lower()} space who want to "
        f"{promise or f'move faster with {topic}'}."
    )

    add_heading("What Makes This Feel Premium")
    add_bullets(sales_bullets)

    add_heading("Core Strategy")
    add_body(
        f"The fastest way to make {topic} feel useful is to reduce overwhelm, tighten the path, "
        "and make the next action obvious. Premium products do not win by being louder. "
        "They win by being clearer."
    )

    add_heading("Step-by-Step Framework")
    add_body("Step 1: Define the exact result.")
    add_body(
        f"Start with a specific goal around {topic}. Broad goals create weak action. "
        f"The narrower the target, the stronger the system feels."
    )
    add_body("Step 2: Remove friction.")
    add_body(
        "Strip away everything that does not move the user closer to the result. "
        "Premium products save time, attention, and decision fatigue."
    )
    add_body("Step 3: Follow a simple execution loop.")
    add_body(
        "Take the first action, review the result, adjust, and repeat. "
        "The product should create motion before it tries to create mastery."
    )

    add_heading("Templates")
    add_bullets([
        f'Prompt: "Build me a beginner-friendly action plan for {topic} in the {niche} niche."',
        f'Prompt: "Create a premium checklist for {buyer.lower()} who want to {promise or f"succeed with {topic}"}."',
        f'Prompt: "Write stronger examples and case-style scenarios for {topic} in a {tone.lower()} tone."',
        f'Prompt: "Turn this material into a premium guide with better flow, confidence, and clarity."',
    ])

    add_heading("Fast-Start Checklist")
    add_bullets([
        "Pick one result and one target user.",
        "Use the simplest version of the framework first.",
        "Take one action immediately.",
        "Review what worked.",
        "Repeat with higher quality, not more chaos.",
    ])

    add_heading("Bonus Materials")
    add_body(
        f"This pack includes bonus material focused on: {bonus or 'prompts, templates, and checklists'}."
    )
    add_bullets([
        "Bonus prompt bank",
        "Bonus expansion ideas",
        "Bonus fast-start worksheet",
        "Bonus premium formatting notes",
        "Bonus future product spin-offs",
    ])

    add_heading("Examples and Expansion")
    for i in range(1, 11):
        add_body(
            f"Expansion Example {i}: A premium product becomes stronger when it makes the next move feel obvious. "
            f"For {topic}, that means giving the reader a direct action path, simple language, and clearer choices."
        )

    story.append(PageBreak())

    add_heading("Deeper Notes")
    for i in range(1, 16):
        add_body(
            f"Advanced Insight {i}: Premium content is not just longer. It is better organized, more confident, "
            f"more selective, and more useful. In {topic}, clarity creates perceived value."
        )

    if notes:
        add_heading("Custom Notes")
        add_body(notes)

    add_heading("Packaging Notes")
    add_bullets([
        "Use bold headers and lots of white space.",
        "Keep each page visually calm.",
        "Package this as a premium shortcut, not just another ebook.",
        "Lead with the outcome and the ease of execution.",
    ])

    doc.build(story)

    file_url = f"{base_url}/api/file/{filename}"

    return {
        "status": "done",
        "mode": "product",
        "title": title,
        "summary": f"Premium PDF created for topic '{topic}'.",
        "file_name": filename,
        "file_url": file_url,
        "preview_url": file_url,
    }
