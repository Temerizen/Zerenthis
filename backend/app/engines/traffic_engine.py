from __future__ import annotations

from typing import Any, Dict, List

def _safe_topic(product: Dict[str, Any]) -> str:
    return (
        product.get("topic")
        or product.get("title")
        or product.get("niche")
        or "digital product"
    )

def generate_traffic_pack(product: Dict[str, Any]) -> Dict[str, Any]:
    topic = _safe_topic(product)
    title = product.get("title", topic)
    checkout_link = product.get("checkout_link", "")

    hooks: List[str] = [
        f"Most people are overcomplicating {topic}.",
        f"This {topic} shortcut can save you weeks.",
        f"If you want faster results with {topic}, start here.",
        f"Nobody talks about this angle for {topic}.",
        f"This is the easiest way to turn {topic} into action."
    ]

    scripts = []
    for i, hook in enumerate(hooks, start=1):
        scripts.append({
            "id": i,
            "hook": hook,
            "script": f"""{hook}

Here is the simple version:
1. Start with a clear outcome.
2. Use the done-for-you framework.
3. Take action today instead of researching forever.

If you want the full system, grab: {title}
{checkout_link}""".strip(),
            "cta": f"Get the full system: {title} {checkout_link}".strip()
        })

    captions = [
        f"Built for speed. Built for results. {title}",
        f"Stop guessing. Start executing. {title}",
        f"Turn attention into action with {title}"
    ]

    hashtags = [
        "#DigitalProducts", "#OnlineIncome", "#FacelessContent",
        "#CreatorBusiness", "#SideHustle", "#AIWorkflow"
    ]

    return {
        "hooks": hooks,
        "scripts": scripts,
        "captions": captions,
        "hashtags": hashtags,
        "posting_plan": [
            "Post 2 TikToks daily",
            "Post 2 YouTube Shorts daily",
            "Repurpose best hook into Instagram Reels",
            "Pin CTA comment with checkout link",
            "Double down on highest-watch-time hook"
        ]
    }
