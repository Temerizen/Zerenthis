from __future__ import annotations

import json
from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.core.control_core import OUTPUT_DIR, append_history, read_control_state, resolve_topic, slugify, write_control_state
from backend.app.engines.product_engine import generate_product
from backend.app.engines.offer_engine import generate_offer
from backend.app.engines.traffic_engine import generate_traffic

router = APIRouter(prefix="/api/full-loop", tags=["full-loop"])

class LoopRequest(BaseModel):
    topic: str | None = None

@router.post("")
def run_full_loop(payload: LoopRequest):
    topic = resolve_topic(payload.topic)

    product = generate_product(topic)
    offer = generate_offer(product)
    traffic = generate_traffic(topic, str(product.get("title", "Premium Digital System")))

    result = {
        "topic": topic,
        "product": product,
        "offer": offer,
        "traffic": traffic,
    }

    filename = f"{slugify(topic)}_full_loop.json"
    path = OUTPUT_DIR / filename
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    state = read_control_state()
    state["active_topic"] = topic
    state["last_product_file"] = str(path)
    state["last_offer_file"] = str(path)
    state["last_traffic_file"] = str(path)
    state["last_full_loop_file"] = str(path)
    write_control_state(state)

    append_history({"event": "full_loop_generated", "topic": topic, "file": str(path)})

    return {
        "status": "full_loop_complete",
        "topic": topic,
        "file": str(path),
        "result": result
    }

