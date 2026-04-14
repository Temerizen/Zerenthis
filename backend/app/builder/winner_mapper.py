from __future__ import annotations

from backend.app.engines.selection_engine import select_winners

def winner_to_targets() -> list[str]:
    winners = select_winners(top_n=2)
    targets: list[str] = []

    for name in winners:
        text = name.lower()

        if "viral" in text or "content" in text:
            targets.extend([
                "backend/app/engines/traffic_engine.py",
                "backend/app/engines/storefront_engine.py",
                "backend/app/engines/offer_engine.py",
            ])
        elif "side hustle" in text or "income" in text:
            targets.extend([
                "backend/app/engines/offer_engine.py",
                "backend/app/engines/conversion_engine.py",
                "backend/app/engines/storefront_engine.py",
            ])

    seen = set()
    ordered = []
    for t in targets:
        if t not in seen:
            seen.add(t)
            ordered.append(t)

    return ordered
