from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import os, uuid

OUT_DIR = "backend/data/outputs"
os.makedirs(OUT_DIR, exist_ok=True)

def build_product_pack(**kwargs):
    topic = kwargs.get("topic", "AI System")
    promise = kwargs.get("promise", "get results fast")
    buyer = kwargs.get("buyer", "beginners")

    filename = f"{topic.replace(' ','_')}_{uuid.uuid4().hex[:6]}.pdf"
    path = os.path.join(OUT_DIR, filename)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path)

    content = []

    def section(title, text):
        content.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
        content.append(Spacer(1,10))
        content.append(Paragraph(text, styles["BodyText"]))
        content.append(Spacer(1,20))

    # COVER
    content.append(Paragraph(f"<b>{topic.upper()} SYSTEM</b>", styles["Title"]))
    content.append(Spacer(1,20))
    content.append(Paragraph(f"A complete system to help {buyer} {promise}", styles["BodyText"]))
    content.append(PageBreak())

    # CORE IDEA
    section("The Core Idea",
    f"""
This system focuses on using AI to generate high-value assets quickly and monetize them.
Instead of building slowly, you create and sell immediately.
    """)

    # MODEL 1
    section("Model 1: Digital Product Engine",
    f"""
Create and sell PDFs using AI.

Steps:
1. Choose a problem in {topic}
2. Generate a premium guide
3. Upload to Gumroad
4. Price between $9–$29
5. Repeat daily

Goal: First sale within days
    """)

    # MODEL 2
    section("Model 2: Faceless Content System",
    """
Use AI to create viral short videos.

Steps:
1. Generate scripts
2. Add AI voice
3. Add captions
4. Post daily

Monetization:
- Affiliate links
- Product funnels
- Traffic conversion
    """)

    # MODEL 3
    section("Model 3: AI Service System",
    """
Sell services using AI.

Examples:
- Resume writing
- Content creation
- Social posts

Steps:
1. Find client
2. Generate work using AI
3. Deliver fast
4. Scale
    """)

    # EXECUTION PLAN
    section("7-Day Execution Plan",
    """
Day 1: Generate 3 products  
Day 2: Upload listings  
Day 3: Create videos  
Day 4: Post content  
Day 5: Improve  
Day 6: Expand  
Day 7: Scale  
    """)

    # PROMPTS
    section("Copy-Paste Prompts",
    f"""
"Create a premium guide about {topic}"

"Generate viral content ideas"

"Write a product description that converts"
    """)

    # PRICING
    section("Pricing Strategy",
    """
Start: $7–$19  
Scale: $29–$49  
Bundles: $79+  
    """)

    # MISTAKES
    section("Mistakes to Avoid",
    """
- Overthinking
- Waiting too long
- Not posting
- Making things too complex
    """)

    # BONUS
    section("Bonus Ideas",
    """
- Bundle products
- Sell templates
- Sell prompts
- Create mini courses
    """)

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

    for i in range(count):
        result = build_product_pack(topic=f"{topic} {i+1}")
        items.append(result)

    return {
        "status": "done",
        "mode": "product_batch",
        "count": len(items),
        "items": items
    }
