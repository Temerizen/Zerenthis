from __future__ import annotations

from typing import Dict, List

def generate_offer(product: Dict[str, object]) -> Dict[str, object]:
    title = str(product.get("title", "Premium Digital System")).strip()
    topic = str(product.get("topic", title)).strip()

    price_suggestion = 29
    offer_stack: List[str] = [
        title,
        "Quick-start implementation checklist",
        "Swipeable templates and prompts",
        "Bonus momentum tracker",
    ]
    bonuses: List[str] = [
        "Fast-start action sheet",
        "Plug-and-play framework notes",
        "Simple weekly review template",
    ]
    urgency_angle = (
        f"Launch this offer while the buyer still feels the pain of {topic} and wants a fast, clean solution."
    )

    return {
        "topic": topic,
        "product_title": title,
        "price_suggestion": price_suggestion,
        "offer_stack": offer_stack,
        "bonuses": bonuses,
        "urgency_angle": urgency_angle,
    }
