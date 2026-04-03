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

def pick_base():
    b = random.choice(BUYERS)
    n = random.choice(NICHES)
    p = random.choice(PRODUCT_TYPES)
    promise = random.choice(PROMISES)
    price = random.choice(PRICES)
    return {
        "buyer": b["buyer"],
        "pain": b["pain"],
        "niche": n["niche"],
        "channel": n["channel"],
        "product_type": p["product_type"],
        "delivery": p["delivery"],
        "promise": promise,
        "price": price,
    }

def build_title(idea):
    niche = idea["niche"]
    product_type = idea["product_type"]
    buyer = idea["buyer"]
    if "beginners" in buyer:
        audience = "Beginners"
    elif "side hustlers" in buyer:
        audience = "Side Hustlers"
    elif "creators" in buyer:
        audience = "Creators"
    else:
        audience = "New Sellers"
    return f"{niche} {product_type} for {audience}"

def build_offer(idea):
    return f"{idea['product_type']} that helps {idea['buyer']} solve this problem: {idea['pain']}."

def build_monetization_path(idea):
    return f"Create content for {idea['channel']} → send traffic to a low-ticket {idea['product_type']} → test clicks and sales."

def build_hooks(idea):
    hooks = []
    for template in random.sample(HOOK_TEMPLATES, k=min(7, len(HOOK_TEMPLATES))):
        hooks.append(template.format(
            buyer=idea["buyer"],
            niche=idea["niche"],
            pain=idea["pain"],
            product_type=idea["product_type"]
        ))
    return hooks

def generate_idea():
    idea = pick_base()
    idea["title"] = build_title(idea)
    idea["offer"] = build_offer(idea)
    idea["monetization_path"] = build_monetization_path(idea)
    idea["hooks"] = build_hooks(idea)
    return idea

def mutate_from_top(mem):
    if not mem.get("top"):
        return generate_idea()

    base = random.choice(mem["top"]).copy()
    mutated = dict(base)

    if random.random() < 0.6:
        b = random.choice(BUYERS)
        mutated["buyer"] = b["buyer"]
        mutated["pain"] = b["pain"]

    if random.random() < 0.5:
        n = random.choice(NICHES)
        mutated["niche"] = n["niche"]
        mutated["channel"] = n["channel"]

    if random.random() < 0.5:
        p = random.choice(PRODUCT_TYPES)
        mutated["product_type"] = p["product_type"]
        mutated["delivery"] = p["delivery"]

    if random.random() < 0.5:
        mutated["promise"] = random.choice(PROMISES)

    if random.random() < 0.5:
        mutated["price"] = random.choice(PRICES)

    mutated["title"] = build_title(mutated)
    mutated["offer"] = build_offer(mutated)
    mutated["monetization_path"] = build_monetization_path(mutated)
    mutated["hooks"] = build_hooks(mutated)
    return mutated

def score_idea(idea):
    score = 0
    title = idea.get("title", "").lower()
    buyer = idea.get("buyer", "").lower()
    pain = idea.get("pain", "").lower()
    offer = idea.get("offer", "").lower()
    niche = idea.get("niche", "").lower()
    hooks = idea.get("hooks", [])

    if len(title) >= 12:
        score += 1
    if any(x in buyer for x in ["beginners", "creators", "side hustlers", "starting from zero"]):
        score += 2
    if len(pain) >= 20:
        score += 2
    if any(x in niche for x in ["youtube shorts", "faceless tiktok", "digital products", "ai content", "affiliate"]):
        score += 2
    if any(x in offer for x in ["helps", "solve", "problem"]):
        score += 1
    if 9 <= int(idea.get("price", 0)) <= 39:
        score += 1
    if len(hooks) >= 5 and all(len(h.strip()) > 20 for h in hooks[:5]):
        score += 1

    return max(1, min(10, score))

def build_product(idea, score):
    hooks_text = "\n".join([f"- {h}" for h in idea["hooks"]])
    return f"""# {idea['title']}

## WHO THIS IS FOR
{idea['buyer']}

## CORE PAIN
{idea['pain']}

## PROMISE
{idea['promise']}

## PRODUCT TO SELL
{idea['offer']}

## PRICE
${idea['price']}

## DELIVERY
{idea['delivery']}

## CHANNEL
{idea['channel']}

## MONETIZATION PATH
{idea['monetization_path']}

## 7 HOOKS
{hooks_text}

## SCORE
{score}/10

## CTA
Launch a smaller, clearer offer and test it fast.
"""

def run_engine():
    mem = load_memory()

    best_result = None
    attempts = []

    for _ in range(3):
        if mem.get("top") and random.random() < 0.7:
            idea = mutate_from_top(mem)
        else:
            idea = generate_idea()

        score = score_idea(idea)
        product = build_product(idea, score)

        result = {
            "idea": idea,
            "score": score,
            "product": product,
            "time": now_iso()
        }
        attempts.append(result)

        if best_result is None or score > best_result["score"]:
            best_result = result

        if score >= 6:
            break

    mem["history"].append(best_result)
    mem["history"] = mem["history"][-150:]

    strong = [x for x in mem["history"] if int(x.get("score", 0)) >= 6]
    strong.sort(key=lambda x: (x.get("score", 0), x.get("time", "")), reverse=True)
    mem["top"] = [x["idea"] for x in strong[:20]]

    save_memory(mem)

    return {
        "idea": best_result["idea"],
        "score": best_result["score"],
        "product": best_result["product"],
        "attempts_considered": len(attempts),
        "top_memory_count": len(mem["top"])
    }
