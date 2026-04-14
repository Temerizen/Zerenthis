import json
import os
import random
from datetime import datetime

MEMORY_PATH = "backend/data/cash_memory.json"
METRICS_PATH = "backend/data/cash_metrics.json"

def now():
    return datetime.utcnow().isoformat()

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs("backend/data", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# =========================
# LOAD SYSTEM DATA
# =========================

def load_memory():
    return load_json(MEMORY_PATH, {"history": [], "top": []})

def save_memory(mem):
    save_json(MEMORY_PATH, mem)

def load_metrics():
    return load_json(METRICS_PATH, {"items": []})

# =========================
# PERFORMANCE INTELLIGENCE
# =========================

def get_performance(idea):
    metrics = load_metrics()

    views = 0
    clicks = 0
    sales = 0

    for m in metrics["items"]:
        if m["idea"].get("title") == idea.get("title"):
            if m["event"] == "view":
                views += m["value"]
            elif m["event"] == "click":
                clicks += m["value"]
            elif m["event"] == "sale":
                sales += m["value"]

    return views, clicks, sales

def performance_score(idea):
    views, clicks, sales = get_performance(idea)

    score = 0

    if views > 0:
        ctr = clicks / max(views, 1)
        score += min(3, int(ctr * 10))

    if clicks > 0:
        conversion = sales / max(clicks, 1)
        score += min(5, int(conversion * 10))

    if sales > 0:
        score += 3  # heavy reward

    return score, {
        "views": views,
        "clicks": clicks,
        "sales": sales
    }

# =========================
# CORE IDEA POOLS
# =========================

BUYERS = [
    "beginners with no audience",
    "side hustlers who need fast cash",
    "creators stuck under 1k views",
    "faceless creators starting from zero"
]

PAINS = [
    "they do not know what to post or how to get a first sale",
    "their content is not converting into clicks",
    "they need a simple monetizable idea fast",
    "they are overwhelmed and not consistent"
]

NICHES = [
    ("Faceless TikTok","TikTok"),
    ("YouTube Shorts","YouTube"),
    ("Digital Products","Gumroad"),
    ("AI Content","X and Gumroad"),
    ("Affiliate Content","TikTok and Gumroad")
]

PRODUCTS = [
    ("Hook Pack","PDF"),
    ("Script Pack","PDF"),
    ("Launch Kit","PDF + Templates"),
    ("Blueprint","PDF"),
    ("Sprint","PDF + Checklist")
]

PROMISES = [
    "launch a monetizable idea in 72 hours",
    "get first traction within a week",
    "build a simple product and test it fast",
    "turn attention into first sales quickly"
]

PRICES = [9,19,29,39]

HOOKS = [
    "Nobody tells {buyer} this about {niche}.",
    "If you are stuck with {pain}, start here.",
    "This is the simplest way to start with {niche}.",
    "Most people overcomplicate {niche}. Do this instead.",
    "You do not need a big audience to make this work.",
    "This mistake kills beginner momentum instantly.",
    "A small product can outperform a big course.",
]

# =========================
# IDEA GENERATION
# =========================

def build_idea():
    niche, channel = random.choice(NICHES)
    buyer = random.choice(BUYERS)
    pain = random.choice(PAINS)
    product, delivery = random.choice(PRODUCTS)

    idea = {
        "buyer": buyer,
        "pain": pain,
        "niche": niche,
        "channel": channel,
        "product_type": product,
        "delivery": delivery,
        "promise": random.choice(PROMISES),
        "price": random.choice(PRICES),
    }

    idea["title"] = f"{niche} {product} for {buyer.split()[0].capitalize()}"
    idea["offer"] = f"{product} to help {buyer} solve: {pain}"
    idea["hooks"] = [h.format(buyer=buyer,niche=niche,pain=pain) for h in random.sample(HOOKS,5)]
    idea["path"] = f"{channel} → link → {product} → sales"

    return idea

# =========================
# MUTATION (WINNER BIAS)
# =========================

def mutate_from_winners(mem):
    winners = []

    for item in mem.get("history", []):
        perf, stats = performance_score(item["idea"])
        if stats["sales"] > 0:
            winners.append(item["idea"])

    if winners:
        base = random.choice(winners)
    elif mem.get("top"):
        base = random.choice(mem["top"])
    else:
        return build_idea()

    idea = dict(base)

    if random.random() < 0.6:
        idea.update(build_idea())

    return idea

# =========================
# SCORING
# =========================

def score_idea(idea, mem):
    base_score = 5

    perf_score, stats = performance_score(idea)

    # reward real money heavily
    score = base_score + perf_score

    # penalize zero traction
    if stats["views"] > 10 and stats["clicks"] == 0:
        score -= 2

    if stats["clicks"] > 10 and stats["sales"] == 0:
        score -= 3

    return max(1, min(10, score))

# =========================
# ENGINE
# =========================

def run_engine():
    mem = load_memory()

    best = None

    for _ in range(5):
        if random.random() < 0.7:
            idea = mutate_from_winners(mem)
        else:
            idea = build_idea()

        score = score_idea(idea, mem)

        result = {
            "idea": idea,
            "score": score,
            "time": now()
        }

        if best is None or score > best["score"]:
            best = result

        if score >= 8:
            break

    mem["history"].append(best)
    mem["history"] = mem["history"][-300:]

    # prioritize real winners
    mem["top"] = sorted(
        mem["history"],
        key=lambda x: performance_score(x["idea"])[0],
        reverse=True
    )[:30]

    save_memory(mem)

    return {
        "idea": best["idea"],
        "score": best["score"],
        "product": best["idea"],
        "message": "system now optimizing for real money",
        "top_count": len(mem["top"])
    }


