import json
import os
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
# METRICS SYSTEM
# =========================

def load_metrics():
    return load_json(METRICS_PATH, {"items": []})

def save_metrics(m):
    save_json(METRICS_PATH, m)

def record_event(idea, event_type, value=1):
    m = load_metrics()

    entry = {
        "idea": idea,
        "event": event_type,  # view / click / sale
        "value": value,
        "time": now()
    }

    m["items"].append(entry)
    m["items"] = m["items"][-1000:]
    save_metrics(m)

    return {"ok": True, "recorded": entry}

# =========================
# PERFORMANCE SCORING
# =========================

def compute_performance_score(idea):
    m = load_metrics()

    views = 0
    clicks = 0
    sales = 0

    for item in m["items"]:
        if item["idea"].get("title") == idea.get("title"):
            if item["event"] == "view":
                views += item["value"]
            elif item["event"] == "click":
                clicks += item["value"]
            elif item["event"] == "sale":
                sales += item["value"]

    score = 0

    if views > 0:
        ctr = clicks / views
        score += min(3, int(ctr * 10))  # up to +3

    if clicks > 0:
        conversion = sales / clicks
        score += min(5, int(conversion * 10))  # up to +5

    if sales > 0:
        score += 2

    return score, {
        "views": views,
        "clicks": clicks,
        "sales": sales
    }

# =========================
# MEMORY INJECTION
# =========================

def inject_performance(mem):
    for item in mem.get("history", []):
        perf_score, stats = compute_performance_score(item["idea"])

        item["real_world"] = {
            "performance_score": perf_score,
            "stats": stats
        }

        # boost or punish
        item["score"] = max(1, min(10, item["score"] + perf_score))

    return mem

# =========================
# PUBLIC API HELPERS
# =========================

def track_view(idea):
    return record_event(idea, "view", 1)

def track_click(idea):
    return record_event(idea, "click", 1)

def track_sale(idea, amount=1):
    return record_event(idea, "sale", amount)

# =========================
# HOOK INTO ENGINE
# =========================

def enhance_memory(mem):
    return inject_performance(mem)


