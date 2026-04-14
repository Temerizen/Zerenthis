import os, json, time, random

DATA_DIR = "backend/data"

def simulate_external_pull():
    # TEMP: replace later with real APIs (TikTok, Reddit, etc.)
    return {
        "views": random.randint(200, 2000),
        "clicks": random.randint(10, 200),
        "conversions": random.randint(0, 10),
        "revenue": random.randint(0, 100)
    }

def run():
    signal = simulate_external_pull()

    out_path = os.path.join(DATA_DIR, "last_real_signal.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(signal, f, indent=2)

    return {
        "status": "real_traffic_fetched",
        "signal": signal,
        "file": out_path
    }

