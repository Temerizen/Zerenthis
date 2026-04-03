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
        json.dump(mem, f, indent=2, ensure_ascii=False)

def now_iso():
    return datetime.utcnow().isoformat()

# =========================
# CORE DATA
# =========================

BUYERS = [
    {"buyer": "beginners with no audience", "pain": "they do not know what to post or how to get a first sale"},
    {"buyer": "creators stuck under 1k views", "pain": "their content is not hooking attention or converting"},
    {"buyer": "side hustlers who need fast cash", "pain": "they need a simple offer they can launch quickly"},
    {"buyer": "faceless creators starting from zero", "pain": "they want content ideas without showing their face"},
]

NICHES = [
    {"niche": "YouTube Shorts", "channel": "YouTube"},
    {"niche": "Faceless TikTok", "channel": "TikTok"},
    {"niche": "AI Content", "channel": "X and Gumroad"},
    {"niche": "Digital Products", "channel": "Gumroad"},
    {"niche": "Affiliate Content", "channel": "TikTok and Gumroad"},
]

PRODUCT_TYPES = [
    {"product_type": "Hook Pack", "delivery": "PDF"},
    {"product_type": "Script Pack", "delivery": "PDF"},
    {"product_type": "Content Blueprint", "delivery": "PDF"},
    {"product_type": "Launch Kit", "delivery": "PDF + Templates"},
    {"product_type": "Monetization Sprint", "delivery": "PDF + Checklist"},
]

PROMISES = [
    "launch a simple monetizable offer in 72 hours",
    "post your first five conversion-focused pieces of content this week",
    "create a starter digital product and begin testing it quickly",
    "build a cleaner path from views to clicks to first sales",
]

PRICES = [9, 19, 29, 39]

HOOK_TEMPLATES = [
    "Nobody tells {buyer} this about {niche}.",
    "This is the simplest way to start with {niche}.",
    "You do not need a big audience to make {niche} work.",
    "Most people overcomplicate {niche}. Do this instead.",
    "If you are stuck with {pain}, start here.",
    "This beginner mistake kills momentum in {niche}.",
    "A small {product_type} can beat a giant course.",
    "This is how to turn attention into a first offer.",
    "If you want faster traction, stop posting random content.",
    "The easiest entry point for {buyer} is smaller than you think.",
]

# =========================
# IDEA BUILDERS
# =========================

def pick_base():
    b = random.choice(BUYERS)
    n = random.choice(NICHES)
    p = random.choice(PRODUCT_TYPES)
    return {
        "buyer": b["buyer"],
        "pain": b["pain"],
        "niche": n["niche"],
        "channel": n["channel"],
        "product_type": p["product_type"],
        "delivery": p["delivery"],
        "promise": random.choice(PROMISES),
        "price": random.choice(PRICES),
    }

def build_title(i):
    return f"{i['niche']} {i['product_type']} for {i['buyer'].split()[0].capitalize()}"

def build_offer(i):
    return f"{i['product_type']} to help {i['buyer']} solve: {i['pain']}"

def build_path(i):
    return f"{i['channel']} content → link → {i['product_type']} → sales"

def build_hooks(i):
    return [
        t.format(
            buyer=i["buyer"],
            niche=i["niche"],
            pain=i["pain"],
            product_type=i["product_type"]
        )
        for t in random.sample(HOOK_TEMPLATES, 7)
    ]

def generate_idea():
    i = pick_base()
    i["title"] = build_title(i)
    i["offer"] = build_offer(i)
    i["monetization_path"] = build_path(i)
    i["hooks"] = build_hooks(i)
    return i

# =========================
# SIMILARITY (ANTI-CLONE)
# =========================

def similarity(a, b):
    score = 0
    if a.get("niche") == b.get("niche"):
        score += 1
    if a.get("buyer") == b.get("buyer"):
        score += 1
    if a.get("product_type") == b.get("product_type"):
        score += 1
    return score  # 0–3

def diversity_penalty(idea, top):
    if not top:
        return 0
    penalties = []
    for t in top:
        penalties.append(similarity(idea, t))
    return max(penalties) if penalties else 0

# =========================
# SCORING
# =========================

def score_idea(i, mem):
    score = 0

    if len(i["pain"]) > 25:
        score += 2
    if "beginner" in i["buyer"] or "side hustlers" in i["buyer"]:
        score += 2
    if i["price"] <= 39:
        score += 1
    if len(i["hooks"]) >= 5:
        score += 1
    if any(x in i["niche"].lower() for x in ["tiktok","youtube","ai","digital"]):
        score += 2

    # diversity penalty
    penalty = diversity_penalty(i, mem.get("top", []))
    if penalty >= 2:
        score -= 3
    elif penalty == 1:
        score -= 1

    return max(1, min(10, score))

# =========================
# MUTATION
# =========================

def mutate(mem):
    if not mem.get("top"):
        return generate_idea()

    base = random.choice(mem["top"])
    i = dict(base)

    if random.random() < 0.6:
        i.update(pick_base())

    i["title"] = build_title(i)
    i["offer"] = build_offer(i)
    i["monetization_path"] = build_path(i)
    i["hooks"] = build_hooks(i)
    return i

# =========================
# PRODUCT
# =========================

def build_product(i, score):
    hooks = "\n".join([f"- {h}" for h in i["hooks"]])
    return f"""# {i['title']}

## WHO
{i['buyer']}

## PAIN
{i['pain']}

## OFFER
{i['offer']}

## PRICE
${i['price']}

## PATH
{i['monetization_path']}

## HOOKS
{hooks}

## SCORE
{score}/10
"""

# =========================
# ENGINE
# =========================

def run_engine():
    mem = load_memory()

    best = None

    for _ in range(4):
        idea = mutate(mem) if random.random() < 0.7 else generate_idea()
        score = score_idea(idea, mem)

        result = {
            "idea": idea,
            "score": score,
            "time": now_iso()
        }

        if best is None or score > best["score"]:
            best = result

        if score >= 7:
            break

    mem["history"].append(best)
    mem["history"] = mem["history"][-200:]

    strong = [x for x in mem["history"] if x["score"] >= 7]
    strong.sort(key=lambda x: x["score"], reverse=True)

    mem["top"] = [x["idea"] for x in strong[:25]]

    save_memory(mem)

    product = build_product(best["idea"], best["score"])

    return {
        "idea": best["idea"],
        "score": best["score"],
        "product": product,
        "top_size": len(mem["top"])
    }
