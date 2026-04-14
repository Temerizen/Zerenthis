import json, os, time

DATA_DIR = "backend/data"

def log_real_signal(topic, views=0, clicks=0, conversions=0, revenue=0):
    path = os.path.join(DATA_DIR, "real_world_signals.json")

    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []
    except:
        data = []

    record = {
        "timestamp": int(time.time()),
        "topic": topic,
        "views": views,
        "clicks": clicks,
        "conversions": conversions,
        "revenue": revenue,
        "real": True
    }

    data.append(record)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return record
