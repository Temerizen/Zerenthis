from pathlib import Path
import json
import time

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "backend" / "data"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"
CURRENT_TOPIC_FILE = DATA_DIR / "current_topic.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def _get_locked_topic(default_topic: str = "default_topic") -> str:
    try:
        if CURRENT_TOPIC_FILE.exists():
            data = json.loads(CURRENT_TOPIC_FILE.read_text(encoding="utf-8"))
            return data.get("topic") or default_topic
    except Exception:
        pass
    return default_topic

def _build_product(topic: str) -> dict:
    title = topic.replace("_", " ").title()
    return {
        "topic": topic,
        "title": title,
        "description": f"A proven system based on {topic} designed to generate results using validated market demand.",
        "steps": [
            "Understand the exact problem this topic solves",
            "Apply a simple repeatable system",
            "Execute daily with minimal friction",
            "Track results and refine based on performance"
        ],
        "value_bullets": [
            "Built from proven revenue-generating ideas",
            "Focused on execution, not theory",
            "Simple system that compounds over time",
            "Easy to package and sell"
        ]
    }

def _write_product_file(topic: str, product: dict) -> str:
    filename = OUTPUT_DIR / f"{topic}_{int(time.time())}.json"
    filename.write_text(json.dumps(product, indent=2), encoding="utf-8")
    return str(filename)

def run_product_engine():
    topic = _get_locked_topic()
    product = _build_product(topic)
    filename = _write_product_file(topic, product)
    return {
        "status": "product_generated",
        "topic": topic,
        "file": filename,
        "product": product
    }

def generate_product(topic: str | None = None):
    chosen_topic = topic or _get_locked_topic()
    product = _build_product(chosen_topic)
    filename = _write_product_file(chosen_topic, product)
    return {
        "status": "product_generated",
        "topic": chosen_topic,
        "file": filename,
        "product": product
    }

def build_product(topic: str | None = None):
    return generate_product(topic)
