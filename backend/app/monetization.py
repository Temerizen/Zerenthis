from fastapi import APIRouter, Body
from datetime import datetime
from pathlib import Path
import os, json

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

PRICING_FILE = DATA_DIR / "pricing_rules.json"

DEFAULT_PRICING = {
    "low_ticket": {"min": 9, "max": 29},
    "mid_ticket": {"min": 39, "max": 99},
    "high_ticket": {"min": 149, "max": 499}
}

def _read_json(path: Path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def _write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _slug(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in (s or "untitled")).strip("_")[:80] or "untitled"

def _write_text(name: str, content: str) -> str:
    path = OUTPUT_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"/api/file/{name}"

def _write_json_output(name: str, data: dict) -> str:
    path = OUTPUT_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return f"/api/file/{name}"

def choose_price(scores: dict, niche: str, buyer: str):
    rules = _read_json(PRICING_FILE, DEFAULT_PRICING)
    monetization = float(scores.get("monetization", 7))
    clarity = float(scores.get("clarity", 7))
    virality = float(scores.get("virality", 7))
    overall = float(scores.get("overall", (monetization + clarity + virality) / 3))

    premium_signal = any(x in (buyer + " " + niche).lower() for x in [
        "business", "founder", "agency", "consultant", "professional", "premium", "b2b"
    ])

    if overall >= 8.5 or (premium_signal and monetization >= 8):
        band = "high_ticket"
    elif overall >= 7.0:
        band = "mid_ticket"
    else:
        band = "low_ticket"

    r = rules.get(band, DEFAULT_PRICING[band])
    recommended = int(round((float(r["min"]) + float(r["max"])) / 2))
    return {"band": band, "recommended_price": recommended, "range": r}

def build_sales_page(topic, buyer, promise, niche, bonus, price):
    return f"""# {topic}

## Who this is for
{buyer}

## What this helps you do
{promise}

## Why this matters
Most people waste time bouncing between ideas. This package gives you a cleaner route in {niche} so you can act faster and with less guesswork.

## What you get
- A focused core asset around: {topic}
- Action-ready angles and positioning
- A simple execution path
- Bonus: {bonus}

## Outcome
You get a clearer path to execution, a stronger offer angle, and ready-to-use material you can deploy immediately.

## Price
${price}

## Call to Action
Get the {topic} package now and start to {promise}.
"""

def build_gumroad_blurb(topic, buyer, promise, price):
    return f"""{topic}

Built for {buyer}.

What it does:
Helps you {promise} with a clean, practical package you can use right away.

Price: ${price}

Buy now and start today.
"""

def build_email_promo(topic, buyer, promise, price):
    subject = f"{topic}: a faster way to {promise}"
    body = f"""Subject: {subject}

If you want a cleaner way to {promise}, this package was built for {buyer}.

Inside, you get a focused asset around {topic}, designed to help you move faster and with more clarity.

Price: ${price}

Reply or grab it now and start today.
"""
    return body

def build_offer_stack(topic, bonus, price_band):
    stacks = {
        "low_ticket": [
            f"{topic} core pack",
            "Quick-start checklist",
            f"Bonus: {bonus}"
        ],
        "mid_ticket": [
            f"{topic} premium pack",
            "Quick-start checklist",
            "Execution roadmap",
            f"Bonus: {bonus}"
        ],
        "high_ticket": [
            f"{topic} authority pack",
            "Execution roadmap",
            "Conversion positioning sheet",
            "Premium implementation notes",
            f"Bonus: {bonus}"
        ]
    }
    return stacks.get(price_band, stacks["mid_ticket"])

@router.post("/api/monetize/package")
def monetize_package(payload: dict = Body(...)):
    topic = payload.get("topic", "Faceless TikTok AI starter pack for beginners")
    buyer = payload.get("buyer", "New creators")
    promise = payload.get("promise", "start posting quickly")
    niche = payload.get("niche", "Content Monetization")
    tone = payload.get("tone", "Premium")
    bonus = payload.get("bonus", "hook templates")
    notes = payload.get("notes", "monetization sweep run")

    try:
        from backend.app.body_engine import build_variants, score_package
    except Exception:
        build_variants = None
        score_package = None

    variants = []
    if build_variants:
        try:
            variants = build_variants(topic, buyer, promise, niche) or []
        except Exception:
            variants = []

    safe_script = (
        f"{topic}\n\nFor: {buyer}\nPromise: {promise}\n"
        "Use one clear outcome, package one strong asset, and sell the simple result."
    )

    scores = {"overall": 7.5, "clarity": 7.5, "virality": 7.0, "monetization": 8.0}
    if score_package:
        try:
            titles = [v.get("title", "") for v in variants if isinstance(v, dict)]
            scores = score_package(topic, buyer, promise, niche, tone, safe_script, titles) or scores
        except Exception:
            pass

    pricing = choose_price(scores, niche, buyer)
    price = pricing["recommended_price"]
    offer_stack = build_offer_stack(topic, bonus, pricing["band"])

    sales_page = build_sales_page(topic, buyer, promise, niche, bonus, price)
    gumroad_blurb = build_gumroad_blurb(topic, buyer, promise, price)
    email_promo = build_email_promo(topic, buyer, promise, price)

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    stem = f"{_slug(topic)}_monetize_{ts}"

    sales_page_url = _write_text(f"{stem}_sales_page.md", sales_page)
    gumroad_url = _write_text(f"{stem}_gumroad.txt", gumroad_blurb)
    email_url = _write_text(f"{stem}_email_promo.txt", email_promo)

    manifest = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "phase": "real money pipeline",
        "input": {
            "topic": topic,
            "buyer": buyer,
            "promise": promise,
            "niche": niche,
            "tone": tone,
            "bonus": bonus,
            "notes": notes
        },
        "scores": scores,
        "pricing": pricing,
        "offer_stack": offer_stack,
        "deliverables": {
            "sales_page_url": sales_page_url,
            "gumroad_blurb_url": gumroad_url,
            "email_promo_url": email_url
        }
    }

    manifest_url = _write_json_output(f"{stem}_manifest.json", manifest)

    return {
        "status": "ok",
        "phase": "real money pipeline",
        "scores": scores,
        "pricing": pricing,
        "offer_stack": offer_stack,
        "sales_page_url": sales_page_url,
        "gumroad_blurb_url": gumroad_url,
        "email_promo_url": email_url,
        "manifest_url": manifest_url
    }

