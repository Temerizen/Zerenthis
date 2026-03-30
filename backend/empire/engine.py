from __future__ import annotations

import json
import random
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EMPIRE_DIR = ROOT / "data" / "empire"
EMPIRE_DIR.mkdir(parents=True, exist_ok=True)

STATE_FILE = EMPIRE_DIR / "state.json"
MEMORY_FILE = EMPIRE_DIR / "memory.json"
TREND_FILE = EMPIRE_DIR / "trendboard.json"
OFFERS_FILE = EMPIRE_DIR / "offers.json"
CONTENT_FILE = EMPIRE_DIR / "content_map.json"
NICHE_FILE = EMPIRE_DIR / "niche_map.json"
REFLECTIONS_FILE = EMPIRE_DIR / "reflections.json"

def _load(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def _save(path: Path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def _now():
    return int(time.time())

def _default_state():
    return {
        "mode": "empire",
        "cycles": 0,
        "focus": [
            "increase perceived value",
            "increase leverage per output",
            "increase conversion potential",
            "increase reusable assets",
            "reduce fragility",
        ],
        "active_niches": [
            "make money online",
            "productivity",
            "ai tools",
            "creator education",
            "digital products",
        ],
        "last_actions": [],
        "compound_score": 0,
    }

def _default_memory():
    return {
        "successful_patterns": [],
        "failed_patterns": [],
        "high_leverage_moves": [],
        "bottlenecks": [],
    }

def _seed_trends():
    return [
        {
            "name": "AI side-income starter kits",
            "angle": "beginner-friendly system",
            "format": "product pack",
            "score": 88,
        },
        {
            "name": "Faceless shorts monetization",
            "angle": "speed and simplicity",
            "format": "shorts pack",
            "score": 84,
        },
        {
            "name": "Micro-offers for creators",
            "angle": "low-ticket bundle ladder",
            "format": "product pack",
            "score": 81,
        },
        {
            "name": "Execution systems for overwhelmed beginners",
            "angle": "clarity over complexity",
            "format": "youtube pack",
            "score": 79,
        },
    ]

def _seed_offers():
    return [
        {
            "id": str(uuid.uuid4()),
            "title": "AI Income Quickstart",
            "type": "front_end",
            "price": 19,
            "niche": "make money online",
            "promise": "launch a simple AI-assisted offer fast",
            "leverage_score": 82,
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Creator Execution Bundle",
            "type": "upsell",
            "price": 49,
            "niche": "creator education",
            "promise": "turn scattered effort into a repeatable content machine",
            "leverage_score": 86,
        },
    ]

def _seed_content_map():
    return {
        "pillars": [
            {
                "name": "beginner wins",
                "angles": [
                    "first $100 online",
                    "simple AI workflows",
                    "easy digital offers",
                ],
            },
            {
                "name": "execution systems",
                "angles": [
                    "stop overthinking",
                    "weekly output loops",
                    "repeatable launch process",
                ],
            },
            {
                "name": "offer stacking",
                "angles": [
                    "front-end + order bump + upsell",
                    "value ladder design",
                    "bundle economics",
                ],
            },
        ]
    }

def _seed_niche_map():
    return [
        {
            "niche": "make money online",
            "pain": "overwhelm and no clear starting path",
            "entry_offer": "execution pack",
            "upsell": "template bundle",
            "score": 91,
        },
        {
            "niche": "productivity",
            "pain": "too much information, too little action",
            "entry_offer": "focus system pack",
            "upsell": "weekly planner vault",
            "score": 78,
        },
        {
            "niche": "ai tools",
            "pain": "tool confusion and no implementation path",
            "entry_offer": "ai workflow pack",
            "upsell": "prompt vault",
            "score": 85,
        },
    ]

def bootstrap():
    if not STATE_FILE.exists():
        _save(STATE_FILE, _default_state())
    if not MEMORY_FILE.exists():
        _save(MEMORY_FILE, _default_memory())
    if not TREND_FILE.exists():
        _save(TREND_FILE, _seed_trends())
    if not OFFERS_FILE.exists():
        _save(OFFERS_FILE, _seed_offers())
    if not CONTENT_FILE.exists():
        _save(CONTENT_FILE, _seed_content_map())
    if not NICHE_FILE.exists():
        _save(NICHE_FILE, _seed_niche_map())
    if not REFLECTIONS_FILE.exists():
        _save(REFLECTIONS_FILE, [])

def _load_outputs():
    out_dir = ROOT / "data" / "outputs"
    if not out_dir.exists():
        return []
    return [p.name for p in out_dir.iterdir() if p.is_file()]

def _top_offer(offers):
    if not offers:
        return None
    return sorted(offers, key=lambda x: x.get("leverage_score", 0), reverse=True)[0]

def run_cycle():
    bootstrap()

    state = _load(STATE_FILE, _default_state())
    memory = _load(MEMORY_FILE, _default_memory())
    trends = _load(TREND_FILE, [])
    offers = _load(OFFERS_FILE, [])
    content = _load(CONTENT_FILE, {})
    niches = _load(NICHE_FILE, [])
    reflections = _load(REFLECTIONS_FILE, [])
    outputs = _load_outputs()

    state["cycles"] += 1

    top_offer = _top_offer(offers)
    top_trend = sorted(trends, key=lambda x: x.get("score", 0), reverse=True)[0] if trends else None
    best_niche = sorted(niches, key=lambda x: x.get("score", 0), reverse=True)[0] if niches else None

    actions = []

    if len(outputs) < 3:
        actions.append("increase_output_pressure")
        memory["bottlenecks"].append("low_output_count")

    if top_offer:
        actions.append(f"double_down_offer:{top_offer['title']}")
        memory["high_leverage_moves"].append(top_offer["title"])

    if top_trend:
        actions.append(f"exploit_trend:{top_trend['name']}")

    if best_niche:
        actions.append(f"prioritize_niche:{best_niche['niche']}")

    if len(memory["failed_patterns"]) > len(memory["successful_patterns"]):
        actions.append("tighten_risk_filters")

    state["compound_score"] = min(
        1000,
        state.get("compound_score", 0)
        + len(outputs)
        + len(actions)
        + (top_offer.get("leverage_score", 0) // 10 if top_offer else 0)
    )

    state["last_actions"] = actions[-10:]

    reflection = {
        "id": str(uuid.uuid4()),
        "created_at": _now(),
        "cycle": state["cycles"],
        "outputs_seen": len(outputs),
        "top_offer": top_offer["title"] if top_offer else None,
        "top_trend": top_trend["name"] if top_trend else None,
        "best_niche": best_niche["niche"] if best_niche else None,
        "actions": actions,
        "compound_score": state["compound_score"],
        "operator_judgment": (
            "Push highest leverage offer, reinforce winning niche, and keep asset production compounding."
        ),
    }

    reflections.append(reflection)

    _save(STATE_FILE, state)
    _save(MEMORY_FILE, memory)
    _save(REFLECTIONS_FILE, reflections[-100:])

    return reflection

if __name__ == "__main__":
    bootstrap()
    while True:
        result = run_cycle()
        print("EMPIRE CYCLE:", result["cycle"], "| SCORE:", result["compound_score"], "| ACTIONS:", result["actions"])
        time.sleep(120)
