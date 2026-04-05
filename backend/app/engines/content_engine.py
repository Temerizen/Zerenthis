import os
import re
from datetime import datetime

OUTPUT_DIR = os.path.join("backend", "outputs")

def _slugify(value: str) -> str:
    value = (value or "untitled").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "untitled"

def build_content_pack(payload: dict) -> dict:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    topic = payload.get("topic", "Untitled Offer")
    niche = payload.get("niche", "General")
    tone = payload.get("tone", "Premium")
    buyer = payload.get("buyer", "General audience")
    promise = payload.get("promise", "Useful result")
    bonus = payload.get("bonus", "")
    notes = payload.get("notes", "")
    channel = payload.get("channel", "multi-platform")

    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    slug = _slugify(topic)
    pack_dir = os.path.join(OUTPUT_DIR, f"{slug}_{stamp}")
    os.makedirs(pack_dir, exist_ok=True)

    offer_text = f"""Zerenthis Offer Sheet

Topic: {topic}
Niche: {niche}
Tone: {tone}
Buyer: {buyer}
Promise: {promise}
Bonus: {bonus}
Notes: {notes}

Core Offer:
A practical, fast-start bundle designed to help the buyer get a visible result quickly.

Suggested Price:
$19 starter / $49 expanded / $99 premium

Suggested CTA:
Get the pack, use the templates, post today, refine tomorrow.
"""

    hooks_text = f"""10 Hooks for {topic}

1. The fastest way to start {topic} is simpler than most people think.
2. If you're stuck in {niche}, use this cleaner move instead.
3. Most beginners overcomplicate this. Start here.
4. This is the easiest way to turn one idea into multiple posts.
5. Want momentum fast? Use this framework.
6. Stop guessing. Use a repeatable format.
7. This helps {buyer} get moving without wasting time.
8. Here is a smarter angle for {topic}.
9. One offer, many content pieces. That is the game.
10. Post this today and improve it tomorrow.
"""

    posts_text = f"""Social Posts for {topic}

Post 1:
People think they need a huge plan to start. They do not.
Start with one clean offer, one clear promise, and one simple post.

Post 2:
The mistake most people make in {niche} is waiting until everything looks perfect.
Useful beats perfect. Published beats hidden.

Post 3:
If I had to restart from zero, I would build one small product around one real buyer problem and turn it into ten pieces of content.

Post 4:
A smart system does not ask for constant inspiration.
It turns one idea into posts, scripts, hooks, and offers.

Post 5:
You do not need more chaos.
You need one repeatable engine.
"""

    email_text = f"""Email Sequence for {topic}

Email 1: The simple starting point
Subject: Start here
Body:
You do not need a huge system to get traction. Start with one focused offer and one useful piece of content.

Email 2: Why this works
Subject: One idea, many assets
Body:
A good content engine multiplies one idea into hooks, posts, scripts, and selling angles.

Email 3: Offer close
Subject: Ready to use the pack?
Body:
Use the templates, publish your first assets, and tighten the system as results come in.
"""

    video_text = f"""Short Video Script for {topic}

Hook:
Most people waste weeks trying to look ready.

Body:
Start with one simple offer.
Turn that offer into hooks.
Turn those hooks into short posts and quick videos.
Publish fast.
Refine after feedback.

CTA:
Use the pack and start posting today.
"""

    landing_text = f"""Landing Page Copy for {topic}

Headline:
Launch a cleaner content system without wasting weeks.

Subheadline:
A practical bundle for {buyer} in {niche} who want speed, simplicity, and a real starting point.

Bullets:
- Ready-to-use hooks
- Social post ideas
- Email starter sequence
- Quick video script
- Offer positioning sheet

CTA:
Get the bundle and start today.
"""

    files = {
        "offer": "offer.txt",
        "hooks": "hooks.txt",
        "posts": "posts.txt",
        "email": "email_sequence.txt",
        "video": "video_script.txt",
        "landing": "landing_page.txt",
    }

    content_map = {
        "offer.txt": offer_text,
        "hooks.txt": hooks_text,
        "posts.txt": posts_text,
        "email_sequence.txt": email_text,
        "video_script.txt": video_text,
        "landing_page.txt": landing_text,
    }

    for filename, content in content_map.items():
        with open(os.path.join(pack_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)

    result_files = []
    for label, filename in files.items():
        result_files.append({
            "label": label,
            "file_name": f"{os.path.basename(pack_dir)}/{filename}",
            "file_url": f"/api/file/{os.path.basename(pack_dir)}/{filename}"
        })

    return {
        "status": "completed",
        "pack_dir": os.path.basename(pack_dir),
        "topic": topic,
        "channel": channel,
        "files": result_files
    }
