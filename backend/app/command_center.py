from fastapi import APIRouter, Body
from datetime import datetime, timezone
import uuid
import random

router = APIRouter(prefix="/api/command", tags=["command"])

def _now():
    return datetime.now(timezone.utc).isoformat()

VIRAL_HOOKS = [
    "This is why nobody talks about this...",
    "You’re doing this wrong and it’s costing you views",
    "I tested this so you don’t have to",
    "Nobody tells beginners this...",
    "This will either blow up or flop. Watch.",
    "If this doesn’t work, nothing will"
]

EMOTIONAL_TRIGGERS = [
    "curiosity gap",
    "status improvement",
    "fear of missing out",
    "identity shift",
    "social proof tension",
    "instant reward"
]

CTA_STYLES = [
    "follow for part 2",
    "comment 'guide' and I’ll send it",
    "save this before it disappears",
    "try this tonight",
    "watch this twice"
]

def generate_viral_script(topic):
    hook = random.choice(VIRAL_HOOKS)
    trigger = random.choice(EMOTIONAL_TRIGGERS)
    cta = random.choice(CTA_STYLES)

    return {
        "hook": f"{hook} ({trigger})",
        "script": [
            hook,
            f"Here’s the truth about {topic}.",
            "Most people overcomplicate this.",
            "Step 1: Do the simplest version first.",
            "Step 2: Focus on speed, not perfection.",
            "Step 3: Repeat what actually works.",
            f"This is how people are growing fast right now with {topic}.",
            cta
        ],
        "caption": f"{topic} but simplified for real results. {cta}",
        "hashtags": [
            "#fyp",
            "#viral",
            "#contentcreator",
            "#tiktokgrowth",
            "#facelesstiktok"
        ]
    }

@router.post("/run")
def run_command(payload: dict = Body(...)):
    prompt = (payload.get("prompt") or "").strip()

    if not prompt:
        return {"status": "error", "error": "prompt is required"}

    scripts = [generate_viral_script(prompt) for _ in range(3)]

    return {
        "status": "ok",
        "phase": "viral engine active",
        "job_id": f"cmd_{uuid.uuid4().hex[:10]}",
        "created_at": _now(),
        "result": {
            "title": f"Viral Content Pack: {prompt}",
            "summary": "High-retention TikTok scripts engineered for attention and growth.",
            "assets": [
                {
                    "type": "viral_scripts",
                    "label": "TikTok Scripts",
                    "url": "/api/file/viral_scripts.json"
                }
            ],
            "content": scripts,
            "next_action": "Pick one script, record immediately, post within 10 minutes."
        }
    }
