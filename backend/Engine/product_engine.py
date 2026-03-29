from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import os, uuid

OUT_DIR = "backend/data/outputs"
os.makedirs(OUT_DIR, exist_ok=True)

def generate_product(topic):

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

    # 🔥 COVER
    content.append(Paragraph(f"<b>{topic.upper()} SYSTEM</b>", styles["Title"]))
    content.append(Spacer(1,20))
    content.append(Paragraph("A Complete Execution Blueprint to Make Money Fast", styles["BodyText"]))
    content.append(PageBreak())

    # 🔥 CORE STRATEGY
    section("The Core Idea",
    f"""
This system focuses on using AI to generate high-value assets quickly and sell them.
Instead of building a brand slowly, you create products instantly and monetize immediately.
    """)

    # 🔥 MODEL 1
    section("Model 1: Digital Product Flipping",
    """
Use AI to generate premium PDFs (guides, playbooks, templates).

Steps:
1. Pick a problem (money, fitness, dating)
2. Generate a full premium guide
3. Upload to Gumroad
4. Price at $9–$29
5. Repeat daily

Tools:
- ChatGPT / Zerenthis
- Gumroad

Goal: First sale within 24–72 hours
    """)

    # 🔥 MODEL 2
    section("Model 2: Faceless Content Engine",
    """
Create short-form videos using AI.

Steps:
1. Generate scripts
2. Use AI voice
3. Use captions
4. Post to TikTok + YouTube Shorts

Monetization:
- Affiliate links
- Digital products
- Traffic funnel

Goal: Build attention → convert to money
    """)

    # 🔥 MODEL 3
    section("Model 3: Service Arbitrage",
    """
Sell AI services without doing the work manually.

Examples:
- Resume writing
- Content writing
- Social media posts

Steps:
1. Find client
2. Generate work using AI
3. Deliver fast
4. Scale

Goal: $100–$500 per client
    """)

    # 🔥 EXECUTION PLAN
    section("7-Day Execution Plan",
    """
Day 1: Pick niche + generate 3 products  
Day 2: Upload + optimize listings  
Day 3: Create 5 videos  
Day 4: Post + track  
Day 5: Improve content  
Day 6: Add more products  
Day 7: Double down on what works  
    """)

    # 🔥 PROMPTS
    section("Copy-Paste AI Prompts",
    """
"Create a premium guide about [topic] that people would pay for."

"Generate 10 viral TikTok ideas about [topic]."

"Write a high-converting product description."
    """)

    # 🔥 PRICING
    section("Pricing Strategy",
    """
Start:
$7–$19 for fast conversions

Scale:
$29–$49 for premium packs

Bundle:
Multiple products → $79+
    """)

    # 🔥 MISTAKES
    section("Mistakes to Avoid",
    """
- Overthinking
- Making things too complex
- Waiting for perfection
- Not uploading consistently
    """)

    # 🔥 BONUS
    section("Bonus Ideas",
    """
- Bundle 5 PDFs together
- Sell templates
- Sell prompt packs
- Create mini-courses
    """)

    doc.build(content)

    return path
