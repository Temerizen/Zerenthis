from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

try:
    from app.engines.bridge_engine import synthesize_product
    from app.engines.publish_engine import publish_product
    from app.engines.traffic_engine import generate_traffic_pack
    from app.engines.offer_engine import build_offer_stack
    from app.engines.storefront_engine import build_storefront
except Exception:
    from ..engines.bridge_engine import synthesize_product
    from ..engines.publish_engine import publish_product
    from ..engines.traffic_engine import generate_traffic_pack
    from ..engines.offer_engine import build_offer_stack
    from ..engines.storefront_engine import build_storefront

router = APIRouter(tags=["monetize"])

class MonetizeIn(BaseModel):
    topic: Optional[str] = "Faceless Content Cashflow Kit"
    niche: Optional[str] = "Content Monetization"
    title: Optional[str] = None
    summary: Optional[str] = None
    promise: Optional[str] = None
    price: Optional[int] = 29
    checkout_link: Optional[str] = "https://example.com/checkout"
    sales_copy: Optional[str] = ""
    file: Optional[str] = None

@router.post("/api/monetize")
def monetize(payload: MonetizeIn) -> Dict[str, Any]:
    seed = payload.model_dump()
    product = synthesize_product(seed)
    publish = publish_product(product)
    traffic = generate_traffic_pack({**product, **publish})
    offers = build_offer_stack({**product, **publish})
    storefront = build_storefront(product, publish, traffic)

    return {
        "status": "success",
        "stage": "MONETIZATION_SWEEP",
        "product": product,
        "publish": publish,
        "offers": offers,
        "traffic": traffic,
        "storefront": storefront
    }

