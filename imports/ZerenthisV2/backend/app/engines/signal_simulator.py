import os, json, random, time

DATA_DIR = "backend/data"

def safe_load(path, default=None):
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def choose_profile():
    # Weighted realism:
    # most cycles are mediocre, some weak, some strong
    roll = random.random()
    if roll < 0.20:
        return "weak"
    if roll < 0.75:
        return "medium"
    return "strong"

def generate_signal(profile=None):
    profile = profile or choose_profile()

    if profile == "weak":
        views = random.randint(150, 900)
        clicks = random.randint(max(5, int(views * 0.01)), max(10, int(views * 0.05)))
        conversions = random.randint(0, max(1, int(clicks * 0.04)))
        revenue = conversions * random.choice([0, 5, 9, 12])
    elif profile == "strong":
        views = random.randint(900, 3500)
        clicks = random.randint(max(40, int(views * 0.06)), max(80, int(views * 0.16)))
        conversions = random.randint(max(3, int(clicks * 0.03)), max(5, int(clicks * 0.10)))
        revenue = conversions * random.choice([9, 19, 29, 39])
    else:
        views = random.randint(400, 1800)
        clicks = random.randint(max(15, int(views * 0.03)), max(25, int(views * 0.10)))
        conversions = random.randint(0, max(2, int(clicks * 0.06)))
        revenue = conversions * random.choice([5, 9, 12, 19])

    ctr = round((clicks / views), 6) if views > 0 else 0.0
    cvr = round((conversions / clicks), 6) if clicks > 0 else 0.0

    return {
        "timestamp": int(time.time()),
        "profile": profile,
        "views": views,
        "clicks": clicks,
        "conversions": conversions,
        "revenue": revenue,
        "simulated": True,
        "preview_ctr": ctr,
        "preview_cvr": cvr
    }

def run(payload=None):
    payload = payload or {}
    forced = payload.get("profile")
    signal = generate_signal(forced)

    out_path = os.path.join(DATA_DIR, "last_simulated_signal.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(signal, f, indent=2)

    return {
        "status": "signal_simulated",
        "file": out_path,
        "signal": signal
    }
