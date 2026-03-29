from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import List, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "data" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value or "zerenthis-output"


def _title_case(text: str) -> str:
    return " ".join(word.capitalize() for word in text.split())


def _safe(text: str, fallback: str) -> str:
    text = (text or "").strip()
    return text if text else fallback


def _make_title(topic: str, promise: str) -> str:
    promise = (promise or "").strip()
    if promise:
        return f"{_title_case(topic)} Blueprint for {promise}"
    return f"{_title_case(topic)} Premium Blueprint"


def _sales_bullets(topic: str, buyer: str, promise: str) -> List[str]:
    return [
        f"A premium step-by-step system for {buyer.lower()}",
        f"A cleaner path to {promise or f'better results with {topic}'}",
        "Templates, prompts, and action frameworks",
        "Case-style examples and premium structure",
        "Built to feel useful immediately, not someday",
    ]


def _section_block(story, heading_style, body_style, title: str, body: str):
    story.append(Paragraph(title, heading_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph(body, body_style))
    story.append(Spacer(1, 10))


def _bullet_block(story, bullet_style, items: List[str]):
    for item in items:
        story.append(Paragraph(f"• {item}", bullet_style))
    story.append(Spacer(1, 10))


def _worksheet_table(title: str, rows: List[List[str]]):
    data = [[title, ""]] + rows
    table = Table(data, colWidths=[2.2 * inch, 4.7 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#F8FAFC")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


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
) -> Dict:
    title = _make_title(topic, promise)
    slug = _slugify(title)
    filename = f"{slug}-{uuid.uuid4().hex[:8]}.pdf"
    path = OUTPUT_DIR / filename

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ZTTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=8,
    )
    subtitle_style = ParagraphStyle(
        "ZTSubtitle",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#334155"),
        spaceAfter=18,
    )
    heading_style = ParagraphStyle(
        "ZTHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=20,
        textColor=colors.HexColor("#111827"),
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "ZTBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.8,
        leading=16,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=8,
    )
    bullet_style = ParagraphStyle(
        "ZTBullet",
        parent=body_style,
        leftIndent=12,
        bulletIndent=0,
        spaceAfter=5,
    )

    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=0.72 * inch,
        rightMargin=0.72 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.72 * inch,
        title=title,
        author="Zerenthis",
    )

    story = []

    subtitle = f"A premium {niche.lower()} guide for {buyer.lower()} in a {tone.lower()} tone."
    sales_bullets = _sales_bullets(topic, buyer, promise)

    story.append(Paragraph("ZERENTHIS", heading_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(subtitle, subtitle_style))
    story.append(
        Paragraph(
            f"Primary Promise: {_safe(promise, f'help the reader move faster with {topic}')}",
            body_style,
        )
    )
    story.append(Spacer(1, 10))
    _bullet_block(story, bullet_style, sales_bullets)
    story.append(PageBreak())

    _section_block(
        story,
        heading_style,
        body_style,
        "What’s Inside",
        "This premium pack is structured to feel clean, usable, and easy to act on. "
        "Use it as a sellable Gumroad asset or as a foundation you expand later.",
    )

    toc_rows = [
        ["1. Core Shift", "Why most people stay stuck and what changes outcomes."],
        ["2. Execution Framework", "A clear sequence the buyer can follow."],
        ["3. Templates", "Prompts, scripts, and reusable frameworks."],
        ["4. Case Examples", "Applied scenarios that make the advice feel real."],
        ["5. Worksheets", "Fill-in sections that raise perceived value."],
        ["6. Bonus Pack", "Expansion ideas, prompts, and upgrade notes."],
    ]
    story.append(_worksheet_table("Contents", toc_rows))
    story.append(PageBreak())

    _section_block(
        story,
        heading_style,
        body_style,
        "1. The Core Shift",
        f"The biggest mistake people make with {topic} is confusing more information with better execution. "
        f"In {niche}, clarity is worth more than volume. The premium move is making the next action obvious.",
    )

    _section_block(
        story,
        heading_style,
        body_style,
        "2. Execution Framework",
        "Step 1: Define the exact result.<br/>"
        "Step 2: Remove friction.<br/>"
        "Step 3: Use a repeatable weekly rhythm.<br/>"
        "Step 4: Review, adjust, and refine after action.",
    )

    _section_block(
        story,
        heading_style,
        body_style,
        "3. Premium Positioning",
        f"This pack is for {buyer.lower()} who want to {_safe(promise, f'get better results with {topic}')}. "
        "Premium positioning does not mean sounding fancy. It means the product feels cleaner, calmer, and more useful.",
    )

    _section_block(
        story,
        heading_style,
        body_style,
        "4. Copy-and-Use Templates",
        f'Prompt 1: "Build me a beginner-friendly system for {topic} in the {niche} niche."<br/>'
        f'Prompt 2: "Create case-style examples for {buyer.lower()} who want to {_safe(promise, f"succeed with {topic}")}."<br/>'
        f'Prompt 3: "Turn this material into a premium worksheet pack with better structure and stronger clarity."',
    )

    _section_block(
        story,
        heading_style,
        body_style,
        "5. Case Example A",
        f"A beginner enters the {topic} space overwhelmed. Instead of trying ten things at once, "
        "they choose one result, one process, and one rhythm. In a week, they have proof instead of confusion.",
    )

    _section_block(
        story,
        heading_style,
        body_style,
        "6. Case Example B",
        f"Someone already knows a lot about {topic} but still stalls. The fix is not more ideas. "
        "The fix is reducing friction, packaging actions more cleanly, and repeating the process until it feels natural.",
    )

    story.append(Paragraph("7. Action Worksheet", heading_style))
    story.append(Spacer(1, 8))
    story.append(
        _worksheet_table(
            "Worksheet",
            [
                ["Target Result", _safe(promise, f"Improve outcomes in {topic}")],
                ["Who This Helps", buyer],
                ["Biggest Friction", "______________________________________________"],
                ["First Action", "______________________________________________"],
                ["Weekly Rhythm", "______________________________________________"],
                ["Review Checkpoint", "______________________________________________"],
            ],
        )
    )
    story.append(Spacer(1, 12))

    _section_block(
        story,
        heading_style,
        body_style,
        "8. Bonus Materials",
        f"This pack includes bonus material focused on {_safe(bonus, 'prompts, templates, and checklists')}. "
        "These are here to increase perceived value and reduce thinking time.",
    )

    _bullet_block(
        story,
        bullet_style,
        [
            "Fast-start checklist",
            "Prompt bank for future expansions",
            "Bonus packaging notes",
            "Bonus spin-off ideas",
            "Upgrade path for a premium version 2",
        ],
    )

    for i in range(1, 9):
        _section_block(
            story,
            heading_style,
            body_style,
            f"Advanced Insight {i}",
            f"Premium content in {topic} becomes stronger when it removes noise, keeps confidence high, and makes action feel smaller. "
            "What the buyer remembers is not how much was said, but how easy the next step felt.",
        )

    if notes:
        _section_block(story, heading_style, body_style, "Custom Notes", notes)

    doc.build(story)

    file_url = f"{base_url}/api/file/{filename}"
    return {
        "status": "done",
        "mode": "product",
        "title": title,
        "summary": f"Premium PDF created for '{topic}'.",
        "file_name": filename,
        "file_url": file_url,
        "preview_url": file_url,
    }


def build_product_batch(
    *,
    topic: str,
    niche: str,
    tone: str,
    buyer: str,
    promise: str,
    bonus: str,
    notes: str,
    base_url: str,
    count: int = 3,
) -> Dict:
    items = []
    for i in range(max(1, min(count, 10))):
        result = build_product_pack(
            topic=f"{topic} {i+1}",
            niche=niche,
            tone=tone,
            buyer=buyer,
            promise=promise,
            bonus=bonus,
            notes=notes,
            base_url=base_url,
        )
        items.append(result)

    return {
        "status": "done",
        "mode": "product_batch",
        "count": len(items),
        "items": items,
    }
