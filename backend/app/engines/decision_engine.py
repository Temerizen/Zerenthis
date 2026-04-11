import json, os, random

DATA_PATH = "backend/data/decision_data.json"

def load():
    if not os.path.exists(DATA_PATH):
        return {"ideas": [], "winners": []}
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

def seed():
    data = load()

    base_ideas = [
        {"idea": "Faceless TikTok AI niche", "score": random.randint(50, 90)},
        {"idea": "Digital product bundle", "score": random.randint(50, 90)},
        {"idea": "AI automation templates", "score": random.randint(50, 90)},
        {"idea": "YouTube shorts engine", "score": random.randint(50, 90)}
    ]

    data["ideas"].extend(base_ideas)
    save(data)
    return base_ideas

def queue():
    data = load()
    return sorted(data["ideas"], key=lambda x: x["score"], reverse=True)

def next_best():
    q = queue()
    return q[0] if q else None

def feedback(idea, score):
    data = load()

    for i in data["ideas"]:
        if i["idea"] == idea:
            i["score"] = int((i["score"] + score) / 2)

            if i["score"] > 85:
                data["winners"].append(i)

    save(data)
    return {"updated": idea, "score": score}

def winners():
    return load()["winners"]
