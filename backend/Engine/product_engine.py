from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from pathlib import Path
import uuid

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "data" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def build_product_pack(**kwargs):
    topic = kwargs.get("topic", "AI System")
    promise = kwargs.get("promise", "get results fast")
    buyer = kwargs.get("buyer", "beginners")

    safe_topic = topic.replace(" ", "_").replace("/", "_")
    filename = f"{safe_topic}_{uuid.uuid4().hex[:6]}.pdf"
    path = OUT_DIR / filename

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(path), pagesize=letter)

    content = []

    def section(title, text):
        content.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
        content.append(Spacer(1, 10))
        content.append(Paragraph(text, styles["BodyText"]))
        content.append(Spacer(1, 20))

    content.append(Paragraph(f"<b>{topic.upper()} SYSTEM</b>", styles["Title"]))
    content.append(Spacer(1, 20))
    content.append(Paragraph(f"A complete system to help {buyer} {promise}", styles["BodyText"]))
    content.append(PageBreak())

    section(
        "The Core Idea",
        "This system focuses on using AI to generate high-value assets quickly and monetize them. "
        "Instead of building slowly, you create and sell immediately."
    )

    section(
        "Model 1: Digital Product Engine",
        f"Create and sell PDFs using AI.\n\n"
        f"Steps:\n"
        f"1. Choose a problem in {topic}\n"
        f"2. Generate a premium guide\n"
        f"3. Upload to Gumroad\n"
        f"4. Price between $9–$29\n"
        f"5. Repeat daily\n\n"
        f"Goal: First sale within days"
    )

    section(
        "Model 2: Faceless Content System",
        "Use AI to create viral short videos.\n\n"
        "Steps:\n"
        "1. Generate scripts\n"
        "2. Add AI voice\n"
        "3. Add captions\n"
        "4. Post daily\n\n"
        "Monetization:\n"
        "- Affiliate links\n"
        "- Product funnels\n"
        "- Traffic conversion"
    )

    section(
        "Model 3: AI Service System",
        "Sell services using AI.\n\n"
        "Examples:\n"
        "- Resume writing\n"
        "- Content creation\n"
        "- Social posts\n\n"
        "Steps:\n"
        "1. Find client\n"
        "2. Generate work using AI\n"
        "3. Deliver fast\n"
        "4. Scale"
    )

    section(
        "7-Day Execution Plan",
        "Day 1: Generate 3 products\n"
        "Day 2: Upload listings\n"
        "Day 3: Create videos\n"
        "Day 4: Post content\n"
        "Day 5: Improve\n"
        "Day 6: Expand\n"
        "Day 7: Scale"
    )

    section(
        "Copy-Paste Prompts",
        f"\"Create a premium guide about {topic}\"\n\n"
        "\"Generate viral content ideas\"\n\n"
        "\"Write a product description that converts\""
    )

    section(
        "Pricing Strategy",
        "Start: $7–$19\n"
        "Scale: $29–$49\n"
        "Bundles: $79+"
    )

    section(
        "Mistakes to Avoid",
        "- Overthinking\n"
        "- Waiting too long\n"
        "- Not posting\n"
        "- Making things too complex"
    )

    section(
        "Bonus Ideas",
        "- Bundle products\n"
        "- Sell templates\n"
        "- Sell prompts\n"
        "- Create mini courses"
    )

    doc.build(content)

    return {
        "status": "done",
        "mode": "product",
        "title": f"{topic} System",
        "file_name": filename,
        "file_url": f"/api/file/{filename}",
        "preview_url": f"/api/file/{filename}"
    }


def build_product_batch(**kwargs):
    topic = kwargs.get("topic", "AI System")
    count = int(kwargs.get("count", 3))
    items = []

    for i in range(max(1, min(count, 10))):
        result = build_product_pack(
            topic=f"{topic} {i+1}",
            promise=kwargs.get("promise", "get results fast"),
            buyer=kwargs.get("buyer", "beginners"),
        )
        items.append(result)

    return {
        "status": "done",
        "mode": "product_batch",
        "count": len(items),
        "items": items
    }
