from __future__ import annotations

from typing import List

from Engine.product_engine import build_product_pack
from Engine.video_engine import build_shorts_video


def build_product_batch(
    *,
    topic: str,
    niche: str,
    tone: str,
    buyer: str,
    promise: str,
    bonus: str,
    notes: str,
    base_url: str,
    count: int = 5,
) -> dict:
    outputs = []
    count = max(1, min(count, 10))

    for i in range(count):
        subtopic = f"{topic} Variation {i + 1}"
        result = build_product_pack(
            topic=subtopic,
            niche=niche,
            tone=tone,
            buyer=buyer,
            promise=promise,
            bonus=bonus,
            notes=notes,
            base_url=base_url,
        )
        outputs.append(result)

    return {
        "status": "done",
        "mode": "product_batch",
        "count": len(outputs),
        "items": outputs,
    }


def build_shorts_batch(
    *,
    topic: str,
    tone: str,
    promise: str,
    duration_seconds: int,
    base_url: str,
    count: int = 5,
) -> dict:
    outputs = []
    count = max(1, min(count, 10))

    for i in range(count):
        subtopic = f"{topic} Angle {i + 1}"
        result = build_shorts_video(
            topic=subtopic,
            tone=tone,
            promise=promise,
            duration_seconds=duration_seconds,
            base_url=base_url,
        )
        outputs.append(result)

    return {
        "status": "done",
        "mode": "shorts_batch",
        "count": len(outputs),
        "items": outputs,
    }

