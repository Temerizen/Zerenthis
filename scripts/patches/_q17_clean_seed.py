import json, time

PATH = "backend/data/pattern_memory.json"

patterns = []

for _ in range(4):
    patterns.append({
        "type": "repetition",
        "focus": "toolbox_strategy",
        "signature": "repetition::toolbox_strategy",
        "count": 1,
        "weight": 1.5,
        "last_seen": time.time(),
        "timestamp": time.time()
    })

with open(PATH, "w", encoding="utf-8") as f:
    json.dump({"patterns": patterns}, f, indent=2)

print("CLEAN SEED COMPLETE", patterns)
