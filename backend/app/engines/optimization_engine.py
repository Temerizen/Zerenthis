from __future__ import annotations
import json, os, time, random
from typing import Dict, Any, List

CONVERSION_PATH = "backend/data/conversion_memory.json"
REVENUE_PATH = "backend/data/revenue_memory.json"
OUTPUT_PATH = "backend/data/optimization_output.json"

HEADLINE_PATTERNS = [
    "Get {result} in {time} without {pain}",
    "The fastest way to {result} even if {objection}",
    "{result} system that works in {time}",
    "How to {result} starting today",
    "Turn {input} into {result} automatically",
    "{result} blueprint used by top performers"
]

RESULTS = [
    "high-converting content",
    "consistent income",
    "viral growth",
    "automated revenue",
    "engagement spikes"
]

TIMES = ["24 hours", "7 days", "30 days"]
PAINS = ["experience", "a team", "guesswork", "burnout"]
INPUTS = ["ideas", "nothing", "basic tools"]

def _load(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def generate_headline() -> str:
    pattern = random.choice(HEADLINE_PATTERNS)
    return pattern.format(
        result=random.choice(RESULTS),
        time=random.choice(TIMES),
        pain=random.choice(PAINS),
        objection=random.choice(PAINS),
        input=random.choice(INPUTS)
    )

def optimize_price(base_price: float, clicks: int) -> float:
    if clicks > 10:
        return round(base_price * 1.2, 2)
    elif clicks > 5:
        return round(base_price * 1.1, 2)
    elif clicks < 2:
        return round(base_price * 0.85, 2)
    return base_price

def run_optimization() -> Dict[str, Any]:
    conversions = _load(CONVERSION_PATH)
    revenue = _load(REVENUE_PATH)

    output = {
        "optimized": [],
        "timestamp": time.time()
    }

    for product, data in conversions.items():
        clicks = data.get("clicks", 0)

        base_price = 19
        if product in revenue:
            base_price = revenue[product].get("price", 19)

        new_price = optimize_price(base_price, clicks)

        variants = []
        for _ in range(3):
            variants.append({
                "headline": generate_headline(),
                "price": new_price
            })

        output["optimized"].append({
            "product": product,
            "clicks": clicks,
            "old_price": base_price,
            "new_price": new_price,
            "variants": variants
        })

    _save(OUTPUT_PATH, output)
    return output
