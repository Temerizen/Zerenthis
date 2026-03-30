from __future__ import annotations

import uuid
from pathlib import Path
from typing import Dict, List

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def _clean(text: str | None, fallback: str = "") -> str:
    value = (text or "").strip()
    return value if value else fallback

def _title_case(text: str) -> str:
    return " ".join(word.capitalize() for word in _clean(text).replace("_", " ").split())

def _premium_title(topic: str, promise: str) -> str:
    topic_tc = _title_case(_clean(topic, "Digital Product"))
    promise_text = _clean(promise)
    if promise_text:
        return f"{topic_tc} Execution Pack for {promise_text}"
    return f"{topic_tc} Execution Pack"

def _offer_ideas(topic: str, buyer: str, promise: str) -> List[Dict[str, str]]:
    topic = _clean(topic, "digital product")
    topic_tc = _title_case(topic)
    buyer_text = _clean(buyer, "Beginners")
    promise_text = _clean(promise, f"get better results with {topic}")
    return [
        {
            "name": f"{topic_tc} Starter Kit",
            "price": "$19-$29",
            "title": f"The {topic_tc} Starter Kit",
            "description": f"A beginner-friendly pack for {buyer_text.lower()} who want to {promise_text}. Includes fast-start steps, templates, prompts, and a low-friction launch path.",
        },
        {
            "name": f"{topic_tc} Premium Blueprint",
            "price": "$29-$49",
            "title": f"{topic_tc} Premium Blueprint",
            "description": f"A deeper system with examples, pricing logic, execution checklists, and copy-paste assets for buyers who want faster and cleaner progress.",
        },
        {
            "name": f"{topic_tc} Bundle",
            "price": "$49-$79",
            "title": f"The Complete {topic_tc} Bundle",
            "description": f"A premium bundled offer combining guide, prompts, templates, and bonus assets into a stronger high-value package.",
        },
    ]

def _sales_angles(topic: str, buyer: str, promise: str) -> List[str]:
    promise_text = _clean(promise, f"get results with {topic}")
    buyer_text = _clean(buyer, "beginners").lower()
    return [
        f"Built for {buyer_text} who want to {promise_text} without wasting weeks on trial and error.",
        "Position this as a shortcut offer: practical, fast to use, and immediately actionable.",
        "Lead with transformation, not features.",
        "Use beginner-safe language and emphasize speed, clarity, and simplicity.",
    ]

def _cta_lines(topic: str) -> List[str]:
    return [
        f"Get the {topic} pack now and start executing today.",
        "Use the templates, prompts, and checklist in one focused sitting.",
        "Launch the first version fast, then improve based on buyer response.",
        "Start with the simple version, collect proof, and turn it into a repeatable offer.",
    ]

def _listing_copy(title: str, buyer: str, promise: str, bonus: str) -> List[str]:
    promise_text = _clean(promise, "move faster with a clear system")
    bonus_text = _clean(bonus, "prompts, templates, and checklists")
    buyer_text = _clean(buyer, "beginners").lower()
    return [
        f"{title} is a practical digital product for {buyer_text} who want to {promise_text}.",
        "It is designed to remove confusion and replace it with a cleaner execution path.",
        f"Inside, buyers get implementation guidance plus {bonus_text}.",
        "This is ideal for Gumroad, Stan, Payhip, or a simple landing-page offer.",
    ]

def _prompt_bank(topic: str, niche: str, buyer: str, promise: str) -> List[str]:
    topic = _clean(topic, "digital products")
    niche = _clean(niche, "online business")
    buyer_text = _clean(buyer, "beginners").lower()
    promise_text = _clean(promise, f"make progress with {topic}")
    return [
        f"Create a premium digital product about {topic} for {buyer_text} in the {niche} niche.",
        f"Write 10 high-converting product titles for {topic}.",
        f"Generate 25 practical prompts someone can use to {promise_text}.",
        f"Create a 7-day action plan for a beginner trying to succeed with {topic}.",
        f"Write a product description that makes {topic} feel actionable and worth paying for.",
        f"List 10 bundle ideas related to {topic} that can increase average order value.",
        f"Create 5 short-form content ideas that promote a {topic} digital product.",
        f"Create 3 value-stack versions of a {topic} offer with pricing anchors and bonus ideas.",
    ]

def _pricing_recommendation(niche: str, tone: str) -> Dict[str, int]:
    niche_l = _clean(niche).lower()
    tone_l = _clean(tone, "premium").lower()

    if any(x in niche_l for x in ["business", "agency", "saas", "marketing", "sales"]):
        prices = {"front_end": 29, "order_bump": 12, "upsell": 59}
    elif any(x in niche_l for x in ["fitness", "wellness", "mindset", "productivity"]):
        prices = {"front_end": 24, "order_bump": 9, "upsell": 49}
    else:
        prices = {"front_end": 19, "order_bump": 9, "upsell": 39}

    if tone_l == "premium":
        prices["front_end"] += 10
        prices["order_bump"] += 3
        prices["upsell"] += 20

    return prices

def _quality_score(topic: str, buyer: str, promise: str, bonus: str, notes: str) -> Dict:
    checks = {
        "has_specific_topic": len(_clean(topic)) >= 4,
        "has_defined_buyer": len(_clean(buyer)) >= 6,
        "has_promise": bool(_clean(promise)),
        "has_bonus": bool(_clean(bonus)),
        "has_notes": bool(_clean(notes)),
    }
    score = int(sum(1 for x in checks.values() if x) / len(checks) * 100)
    return {"score": score, "checks": checks}

def _make_pdf(title: str, content: str, filename: str) -> Path:
    path = OUTPUT_DIR / filename
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, title)
    y -= 30
    c.setFont("Helvetica", 10)

    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        if not line:
            y -= 10
            continue
        chunks = [line[i:i+95] for i in range(0, len(line), 95)] or [""]
        for chunk in chunks:
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 50
            c.drawString(50, y, chunk)
            y -= 14

    c.save()
    return path

def build_product_pack(
    topic: str,
    niche: str,
    tone: str,
    buyer: str,
    promise: str = "",
    bonus: str = "",
    notes: str = "",
    base_url: str = "",
):
    topic_text = _clean(topic, "Digital Product")
    niche_text = _clean(niche, "Online Business")
    tone_text = _clean(tone, "Premium")
    buyer_text = _clean(buyer, "Beginners starting from zero")
    promise_text = _clean(promise, f"get better results with {topic_text}")
    bonus_text = _clean(bonus, f"{topic_text.title()} Quick-Start Bonus")
    notes_text = _clean(notes, "Keep it practical and premium.")

    title = _premium_title(topic_text, promise_text)
    prices = _pricing_recommendation(niche_text, tone_text)
    front_end_price = prices["front_end"]
    order_bump_price = prices["order_bump"]
    upsell_price = prices["upsell"]
    bundle_total = front_end_price + order_bump_price + upsell_price
    quality = _quality_score(topic_text, buyer_text, promise_text, bonus_text, notes_text)

    filename = f"{topic_text.replace(' ', '_')}_{uuid.uuid4().hex[:6]}.pdf"
    file_url = f"{base_url}/api/file/{filename}" if base_url else f"/api/file/{filename}"

    content = f"""
TITLE
{title}

POSITIONING
Topic: {topic_text}
Niche: {niche_text}
Tone: {tone_text}
Buyer: {buyer_text}
Promise: {promise_text}
Bonus: {bonus_text}

QUALITY SCORE
Score: {quality['score']}

OFFER STACK
1. Front-End Offer: {title} - ${front_end_price}
2. Order Bump: {bonus_text} - ${order_bump_price}
3. Upsell: {_title_case(topic_text)} Bundle - ${upsell_price}
4. Full Cart Value: ${bundle_total}

LISTING COPY
- {_listing_copy(title, buyer_text, promise_text, bonus_text)[0]}
- {_listing_copy(title, buyer_text, promise_text, bonus_text)[1]}
- {_listing_copy(title, buyer_text, promise_text, bonus_text)[2]}
- {_listing_copy(title, buyer_text, promise_text, bonus_text)[3]}

CTA
- {_cta_lines(topic_text)[0]}
- {_cta_lines(topic_text)[1]}
- {_cta_lines(topic_text)[2]}
- {_cta_lines(topic_text)[3]}

SALES ANGLES
- {_sales_angles(topic_text, buyer_text, promise_text)[0]}
- {_sales_angles(topic_text, buyer_text, promise_text)[1]}
- {_sales_angles(topic_text, buyer_text, promise_text)[2]}
- {_sales_angles(topic_text, buyer_text, promise_text)[3]}

PROMPT BANK
- {_prompt_bank(topic_text, niche_text, buyer_text, promise_text)[0]}
- {_prompt_bank(topic_text, niche_text, buyer_text, promise_text)[1]}
- {_prompt_bank(topic_text, niche_text, buyer_text, promise_text)[2]}
- {_prompt_bank(topic_text, niche_text, buyer_text, promise_text)[3]}

FOUNDER NOTES
{notes_text}

DELIVERY
{file_url}
"""
    _make_pdf(title, content, filename)

    return {
        "title": title,
        "file_name": filename,
        "file_url": file_url,
        "offer": {
            "front_end": {"name": title, "price": front_end_price},
            "order_bump": {"name": bonus_text, "price": order_bump_price},
            "upsell": {"name": f"{_title_case(topic_text)} Bundle", "price": upsell_price},
            "bundle_cart_value": bundle_total,
        },
        "summary": {
            "buyer": buyer_text,
            "promise": promise_text,
            "cta": "Start with the front-end offer, add the bonus, and upgrade to the bundle.",
            "quality_score": quality["score"],
            "quality_checks": quality["checks"],
        },
    }

def build_product_batch(**kwargs):
    count = int(kwargs.get("count", 3) or 3)
    base_topic = kwargs.get("topic", "Digital Product")
    results = []

    for i in range(count):
        batch_kwargs = dict(kwargs)
        batch_kwargs["topic"] = f"{base_topic} Pack {i + 1}" if count > 1 else base_topic
        notes = _clean(batch_kwargs.get("notes", ""))
        variant_note = f"Variant: Pack {i + 1}"
        batch_kwargs["notes"] = f"{notes}\n{variant_note}".strip() if notes else variant_note
        results.append(build_product_pack(**batch_kwargs))

    return results

