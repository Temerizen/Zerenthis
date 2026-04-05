from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / "outputs" / "publish"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def slugify(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "product"

def build_sales_copy(product: Dict[str, Any]) -> str:
    title = product.get("title", "Untitled Offer")
    summary = product.get("summary", "A premium digital product.")
    bullets = product.get("steps") or product.get("bullets") or []
    bullet_lines = "\n".join([f"- {b}" for b in bullets[:6]]) if bullets else "- Instant access\n- Clear outcome\n- Built for speed"
    return f"""{title}

{summary}

What you get:
{bullet_lines}

Why it sells:
- Fast result
- Clear promise
- Simple implementation
- Immediate value

Call to action:
Get instant access now.
""".strip()

def publish_product(product: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    title = product.get("title", "Untitled Product")
    slug = slugify(title)
    price = int(product.get("price") or 29)
    summary = product.get("summary", "A premium digital product.")
    checkout_link = product.get("checkout_link") or ""
    sales_copy = product.get("sales_copy") or build_sales_copy(product)

    listing = {
        "slug": slug,
        "title": title,
        "summary": summary,
        "price": price,
        "currency": product.get("currency", "USD"),
        "checkout_link": checkout_link,
        "sales_copy": sales_copy,
        "file": product.get("file"),
        "thumbnail": product.get("thumbnail"),
        "tags": product.get("tags", []),
        "publish_mode": "manual_ready",
        "created_at": now,
        "platform_targets": ["gumroad", "stripe", "website"]
    }

    out_file = OUTPUT_DIR / f"{slug}_{now}.json"
    out_file.write_text(json.dumps(listing, indent=2, ensure_ascii=False), encoding="utf-8")

    listing["publish_file"] = str(out_file).replace("\\", "/")
    listing["gumroad_ready"] = {
        "name": title,
        "price": price,
        "description": sales_copy,
        "url_hint": checkout_link
    }
    return listing
