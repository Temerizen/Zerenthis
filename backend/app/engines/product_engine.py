import json
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "backend" / "data"
PRODUCT_DIR = DATA_DIR / "products"
PRODUCTS_FILE = PRODUCT_DIR / "products.json"

PRODUCT_DIR.mkdir(parents=True, exist_ok=True)

def load_json(p, default):
    try:
        if p.exists():
            return json.loads(p.read_text())
    except:
        pass
    return default

def save_json(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")

def slugify(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_")

def run(payload):
    products = load_json(PRODUCTS_FILE, [])

    topic = payload.get("topic") or "AI Starter Product Pack"
    niche = payload.get("niche") or "Content Monetization"
    slug = slugify(topic)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    guide_name = f"{slug}_guide_{stamp}.txt"
    hooks_name = f"{slug}_hooks_{stamp}.txt"
    offer_name = f"{slug}_offer_{stamp}.txt"

    guide_path = PRODUCT_DIR / guide_name
    hooks_path = PRODUCT_DIR / hooks_name
    offer_path = PRODUCT_DIR / offer_name

    guide_text = f"""# {topic}

Niche: {niche}

This is a starter guide for the product:
- Core promise
- Setup steps
- Audience angle
- Monetization path
"""

    hooks_text = f"""HOOKS FOR: {topic}

1. The fastest way to start with {niche}
2. Most beginners make this mistake in {niche}
3. How to turn {topic} into something sellable
4. The simple system behind better results
"""

    offer_text = f"""OFFER FOR: {topic}

Who this is for:
- beginners
- creators
- side hustlers

What they get:
- guide
- hooks
- offer copy

Outcome:
A ready-to-use digital starter asset.
"""

    guide_path.write_text(guide_text, encoding="utf-8")
    hooks_path.write_text(hooks_text, encoding="utf-8")
    offer_path.write_text(offer_text, encoding="utf-8")

    product = {
        "id": uuid4().hex,
        "title": topic,
        "niche": niche,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": [
            str(guide_path.name),
            str(hooks_path.name),
            str(offer_path.name)
        ],
        "status": "built"
    }

    products.append(product)
    save_json(PRODUCTS_FILE, products)

    return {
        "status": "built",
        "product": product,
        "total_products": len(products),
        "output_dir": str(PRODUCT_DIR)
    }