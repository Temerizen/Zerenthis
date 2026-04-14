import json, os, time

DATA_PATH = "backend/data/pattern_memory.json"

data = {"patterns": []}

for _ in range(3):
    data["patterns"].append({
        "type": "repetition",
        "focus": "toolbox_strategy",
        "strength": 3,
        "timestamp": time.time()
    })

with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("seeded_pattern_memory", data)
