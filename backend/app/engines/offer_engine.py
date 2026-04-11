from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parents[2]
OFFERS_DIR = BASE_DIR / "outputs" / "offers"
OFFERS_DIR.mkdir(parents=True, exist_ok=True)

def build_offer_stack(product: Dict[str, Any]) -> Dict[str, Any]:
    title = product.get("title", "Untitled Product")
    base_price = int(product.get("price") or 29)

    stack = {
        "core_offer": {
            "name": title,
            "price": base_price,
            "type": "entry"
        },
        "upsell": {
            "name": f"{title} Pro Upgrade",
            "price": max(base_price + 20, 49),
            "type": "upsell"
        },
        "bundle": {
            "name": f"{title} Full Bundle",
            "price": max(base_price + 70, 99),
            "type": "bundle"
        }
    }

    out = OFFERS_DIR / f"offer_stack_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(stack, indent=2), encoding="utf-8")

    return {
        "ok": True,
        "offer_file": str(out).replace("\\", "/"),
        "stack": stack
    }
