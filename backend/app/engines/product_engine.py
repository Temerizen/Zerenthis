import json
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "backend" / "data"
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
    p.write_text(json.dumps(data, indent=2))

def run(payload):
    products = load_json(PRODUCTS_FILE, [])

    topic = payload.get("topic") or "AI Starter Product Pack"
    niche = payload.get("niche") or "Content Monetization"

    product = {
        "id": uuid4().hex,
        "title": topic,
        "niche": niche,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": [
            f"{topic.lower().replace(' ', '_')}_guide.txt",
            f"{topic.lower().replace(' ', '_')}_hooks.txt",
            f"{topic.lower().replace(' ', '_')}_offer.txt"
        ],
        "status": "built"
    }

    products.append(product)
    save_json(PRODUCTS_FILE, products)

    return {
        "status": "built",
        "product": product,
        "total_products": len(products)
    }