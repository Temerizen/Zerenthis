import json, time

PATH = "backend/data/pattern_memory.json"

with open(PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Force patterns to look 5 hours old
for p in data.get("patterns", []):
    p["last_seen"] = time.time() - (5 * 3600)

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("FORCED AGING COMPLETE")
