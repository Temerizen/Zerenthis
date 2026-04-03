import json
import os
import random
from datetime import datetime

MEMORY_PATH = "backend/data/cash_memory.json"

def load_memory():
    if not os.path.exists(MEMORY_PATH):
        return {"history": [], "top": []}
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(mem):
    os.makedirs("backend/data", exist_ok=True)
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2)

# =========================
# 🧠 IDEA GENERATION (FREEFORM)
# =========================

def generate_idea():
    verbs = ["Launch", "Explode", "Scale", "Print", "Hack"]
    outcomes = ["Cash", "Sales", "Views", "Followers", "Revenue"]
    angles = ["System", "Kit", "Blueprint", "Engine", "Sprint"]

    title = f"{random.choice(verbs)} {random.choice(outcomes)} with a {random.choice(angles)}"

    niche = random.choice([
        "TikTok", "AI Content", "Affiliate Marketing",
        "Digital Products", "YouTube Shorts"
    ])

    buyer = random.choice([
        "beginners", "creators stuck under 1k views",
        "people with no audience", "side hustlers"
    ])

    return {
        "title": f"{niche} {title}",
        "buyer": buyer,
        "niche": niche,
        "price": random.choice([9,19,29,39])
    }

# =========================
# ⚖️ SCORING ENGINE
# =========================

def score_idea(idea):
    score = 0

    # urgency
    if "cash" in idea["title"].lower():
        score += 2

    # beginner friendliness
    if "beginner" in idea["buyer"]:
        score += 1

    # monetization potential
    if idea["price"] <= 39:
        score += 1

    # niche popularity
    if idea["niche"] in ["TikTok", "AI Content"]:
        score += 2

    return score

# =========================
# 🧬 MUTATION ENGINE
# =========================

def mutate_from_top(mem):
    if not mem["top"]:
        return generate_idea()

    base = random.choice(mem["top"])
    mutated = base.copy()

    if random.random() < 0.5:
        mutated["price"] = random.choice([9,19,29,39])

    if random.random() < 0.5:
        mutated["buyer"] = generate_idea()["buyer"]

    mutated["title"] += " V2"

    return mutated

# =========================
# 🏗️ PRODUCT BUILDER
# =========================

def build_product(idea):
    hooks = "\n".join([f"- Hook {i+1}: Viral angle for {idea['niche']}" for i in range(10)])

    return f"""
# {idea['title']}

## WHO THIS IS FOR
{idea['buyer']}

## FAST RESULT
Get your first traction within 48 hours.

## VIRAL NICHE
{idea['niche']}

## 10 HOOKS
{hooks}

## PRODUCT TO SELL
Price: ${idea['price']}

## MONETIZATION
Post → Views → Link → Sales

## CTA
Start now.
"""

# =========================
# 🔁 MAIN EVOLUTION LOOP
# =========================

def run_engine():
    mem = load_memory()

    if random.random() < 0.7:
        idea = mutate_from_top(mem)
    else:
        idea = generate_idea()

    score = score_idea(idea)

    mem["history"].append({
        "idea": idea,
        "score": score,
        "time": datetime.utcnow().isoformat()
    })

    mem["history"] = mem["history"][-100:]

    top_sorted = sorted(mem["history"], key=lambda x: x["score"], reverse=True)
    mem["top"] = [x["idea"] for x in top_sorted[:10]]

    save_memory(mem)

    product = build_product(idea)

    return {
        "idea": idea,
        "score": score,
        "product": product
    }
