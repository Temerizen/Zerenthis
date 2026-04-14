from __future__ import annotations
import json, os, time
from typing import Dict, Any, List

PROMOTION_PATH = "backend/data/promotion_output.json"
AUTO_SIGNAL_PATH = "backend/data/auto_captured_signals.json"

PLATFORM_WEIGHTS = {
    "reddit": 1.3,
    "twitter": 1.0,
    "tiktok": 1.5,
    "discord": 0.9,
}

CTA_WEIGHTS = {
    "dm me": 1.4,
    "comment": 1.2,
    "say": 1.1,
    "link in bio": 1.0,
    "check this out": 0.9,
}

def _load(path: str):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _load_list(path: str):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _infer_signal_type(content: str) -> str:
    text = (content or "").lower()
    if "dm me" in text:
        return "dm_intent"
    if "comment" in text:
        return "comment_intent"
    if "link in bio" in text:
        return "click_intent"
    if "say " in text:
        return "reply_intent"
    return "interest"

def _infer_weight(platform: str, content: str) -> float:
    p = PLATFORM_WEIGHTS.get((platform or "").lower(), 1.0)
    text = (content or "").lower()

    cta_weight = 1.0
    for key, value in CTA_WEIGHTS.items():
        if key in text:
            cta_weight = value
            break

    return round(p * cta_weight, 2)

def run_auto_signal_capture() -> Dict[str, Any]:
    promotion = _load(PROMOTION_PATH)
    existing = _load_list(AUTO_SIGNAL_PATH)
    if not isinstance(existing, list):
        existing = []

    posts = promotion.get("posts", [])
    product = promotion.get("product", "Unknown")

    captured: List[Dict[str, Any]] = []

    for idx, post in enumerate(posts):
        if not isinstance(post, dict):
            continue

        platform = post.get("platform", "unknown")
        content = post.get("content", "")
        signal_type = _infer_signal_type(content)
        value = _infer_weight(platform, content)

        row = {
            "product": post.get("product", product),
            "source": platform,
            "signal_type": signal_type,
            "value": value,
            "note": "auto_captured_from_promotion",
            "content_preview": content[:120],
            "capture_index": idx,
            "timestamp": time.time(),
        }
        captured.append(row)
        existing.append(row)

    existing = existing[-500:]

    output = {
        "status": "ok",
        "mode": "auto_signal_capture",
        "product": product,
        "captured_count": len(captured),
        "captured": captured,
        "total_stored": len(existing),
        "timestamp": time.time(),
    }

    _save(AUTO_SIGNAL_PATH, existing)
    return output
