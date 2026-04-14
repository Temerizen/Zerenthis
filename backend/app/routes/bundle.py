from __future__ import annotations

import json
from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.core.control_core import OUTPUT_DIR, append_history, read_control_state, resolve_topic, slugify, write_control_state
from backend.app.engines.product_engine import generate_product
from backend.app.engines.offer_engine import generate_offer
from backend.app.engines.traffic_engine import generate_traffic

router = APIRouter(prefix="/api/bundle", tags=["bundle"])

class BundleRequest(BaseModel):
    topic: str | None = None

@router.post("/generate")
def generate_bundle(payload: BundleRequest):
    topic = resolve_topic(payload.topic)
    product = generate_product(topic)
    offer = generate_offer(product)
    traffic = generate_traffic(topic, str(product.get("title", "Premium Digital System")))

    bundle = {
        "topic": topic,
        "product": product,
        "offer": offer,
        "traffic": traffic,
    }

    stem = slugify(topic)
    json_path = OUTPUT_DIR / f"{stem}_bundle.json"
    pdf_path = OUTPUT_DIR / f"{stem}_bundle.pdf"

    json_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")

    pdf_status = "not_attempted"
    pdf_error = None
    try:
        from backend.app.engines.export_engine import export_product_pdf
        export_product_pdf(bundle, str(pdf_path))
        pdf_status = "generated"
    except Exception as e:
        pdf_status = "failed"
        pdf_error = str(e)

    state = read_control_state()
    state["active_topic"] = topic
    state["last_product_file"] = str(json_path)
    state["last_offer_file"] = str(json_path)
    state["last_traffic_file"] = str(json_path)
    state["last_full_loop_file"] = str(json_path)
    write_control_state(state)

    append_history({
        "event": "bundle_generated",
        "topic": topic,
        "json_file": str(json_path),
        "pdf_file": str(pdf_path),
        "pdf_status": pdf_status
    })

    return {
        "status": "bundle_generated",
        "topic": topic,
        "json_file": str(json_path),
        "pdf_file": str(pdf_path),
        "pdf_status": pdf_status,
        "pdf_error": pdf_error,
        "bundle": bundle
    }

