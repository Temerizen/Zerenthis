import os
import time
from backend.app.engines.performance_engine import leaderboard

OUTPUT_DIR = "backend/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_best_output():
    ranked = leaderboard()

    if not ranked:
        return {"status": "no_ranked_topics"}

    top = ranked[0]
    topic = top["topic"]

    content = f"""ZERENTHIS GENERATED ASSET

Top Topic:
{topic}

Average Score:
{top['avg_score']}

Best Score:
{top['best_score']}

Positioning:
This topic is currently the strongest survivor in the system.

Offer Angle:
Use this as the core concept for a digital product, content funnel, or monetized asset.

Suggested Headline:
{topic.title()}

Suggested Hook:
A practical system designed to deliver fast, measurable results.

Suggested CTA:
Turn this winning topic into a premium product, lead magnet, or automated content series.
"""

    file_name = f"winner_{int(time.time())}.txt"
    file_path = os.path.join(OUTPUT_DIR, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "status": "output_generated",
        "topic": topic,
        "file": file_path
    }


