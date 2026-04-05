from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

try:
    from app.engines.bridge_engine import synthesize_product
    from app.engines.publish_engine import publish_product
    from app.engines.traffic_engine import generate_traffic_pack
    from app.engines.feedback_engine import log_feedback
except Exception:
    from ..engines.bridge_engine import synthesize_product
    from ..engines.publish_engine import publish_product
    from ..engines.traffic_engine import generate_traffic_pack
    from ..engines.feedback_engine import log_feedback

router = APIRouter(tags=["full-cycle"])

class FullCycleIn(BaseModel):
    topic: Optional[str] = "Faceless Content Cashflow Kit"
    niche: Optional[str] = "Content Monetization"
    title: Optional[str] = None
    summary: Optional[str] = None
    promise: Optional[str] = None
    price: Optional[int] = 29
    checkout_link: Optional[str] = ""
    sales_copy: Optional[str] = ""
    file: Optional[str] = None

@router.post("/api/full-cycle")
def run_full_cycle(payload: FullCycleIn) -> Dict[str, Any]:
    seed = payload.model_dump()
    product = synthesize_product(seed)
    publish = publish_product(product)
    traffic = generate_traffic_pack({**product, **publish})

    feedback = log_feedback({
        "topic": seed.get("topic"),
        "title": product.get("title"),
        "price": publish.get("price"),
        "checkout_link": publish.get("checkout_link"),
        "publish_file": publish.get("publish_file")
    })

    return {
        "status": "success",
        "stage": "FINAL_INTEGRATION_SELL_SYSTEM_PLUS_LOOP",
        "product": product,
        "publish": publish,
        "traffic": traffic,
        "feedback": feedback
    }
