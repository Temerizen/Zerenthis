import json
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parents[1]
DATA = Path("/data") if Path("/data").exists() else BASE / "backend" / "data"

AUTO = DATA / "autopilot"
CORE = DATA / "core"
MARKET = DATA / "marketplace"

WINNERS = AUTO / "winners.json"
ROADMAP = CORE / "roadmap.json"
INSIGHTS = CORE / "insights.json"
LISTINGS = MARKET / "listings.json"

def read(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def build_insights():
    winners = read(WINNERS, [])

    modules = Counter()
    niches = Counter()
    buyers = Counter()

    for w in winners:
        modules[w.get("module", "unknown")] += 1
        payload = w.get("payload", {}) or {}
        niches[payload.get("niche", "unknown")] += 1
        buyers[payload.get("buyer", "unknown")] += 1

    insights = {
        "top_modules": modules.most_common(),
        "top_niches": niches.most_common(),
        "top_buyers": buyers.most_common(),
        "total_winners": len(winners)
    }

    write(INSIGHTS, insights)
    return insights

def build_roadmap(insights):
    preferred = []
    for name, _score in insights.get("top_modules", []):
        preferred.append({"name": name, "risk": "low", "status": "pending"})

    defaults = [
        {"name": "Money Engine", "risk": "low", "status": "pending"},
        {"name": "Content Factory", "risk": "low", "status": "pending"},
        {"name": "Video Engine", "risk": "low", "status": "pending"},
        {"name": "Founder Console", "risk": "low", "status": "pending"},
        {"name": "AI School", "risk": "medium", "status": "pending"},
        {"name": "Research Engine", "risk": "medium", "status": "pending"},
        {"name": "Cognitive Lab", "risk": "medium", "status": "pending"}
    ]

    seen = set()
    merged = []
    for item in preferred + defaults:
        name = str(item.get("name", "")).strip()
        if not name or name in seen:
            continue
        seen.add(name)
        merged.append(item)

    roadmap = {
        "modules": merged,
        "last_updated": "auto"
    }

    write(ROADMAP, roadmap)
    return roadmap

def build_listings():
    winners = read(WINNERS, [])
    listings = []

    for w in winners:
        result = w.get("result", {}) or {}
        offer = result.get("offer", {}) or {}
        summary = result.get("summary", {}) or {}
        title = result.get("title") or w.get("file_name") or "Untitled Product"

        listing = {
            "module": w.get("module"),
            "job_id": w.get("job_id"),
            "title": title,
            "file_name": w.get("file_name"),
            "file_url": w.get("file_url"),
            "score": w.get("score", 0),
            "front_end_name": (offer.get("front_end") or {}).get("name", title),
            "front_end_price": (offer.get("front_end") or {}).get("price", 29),
            "order_bump_name": (offer.get("order_bump") or {}).get("name", ""),
            "order_bump_price": (offer.get("order_bump") or {}).get("price", 12),
            "upsell_name": (offer.get("upsell") or {}).get("name", ""),
            "upsell_price": (offer.get("upsell") or {}).get("price", 59),
            "buyer": summary.get("buyer", ""),
            "promise": summary.get("promise", ""),
            "cta": summary.get("cta", ""),
            "market_status": "ready_to_list"
        }
        listings.append(listing)

    write(LISTINGS, listings)
    return listings

def run():
    insights = build_insights()
    roadmap = build_roadmap(insights)
    listings = build_listings()

    print("=== ASCENSION UPDATE ===")
    print(json.dumps({
        "insights": insights,
        "roadmap_modules": len(roadmap.get("modules", [])),
        "listing_count": len(listings)
    }, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run()
