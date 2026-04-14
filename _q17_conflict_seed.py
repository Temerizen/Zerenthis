import json, time

PATH = "backend/data/pattern_memory.json"
now = time.time()

data = {
    "patterns": [
        {
            "type": "repetition",
            "focus": "toolbox_strategy",
            "signature": "repetition::toolbox_strategy",
            "count": 1,
            "weight": 1.8,
            "last_seen": now,
            "timestamp": now
        },
        {
            "type": "repetition",
            "focus": "toolbox_strategy",
            "signature": "repetition::toolbox_strategy",
            "count": 1,
            "weight": 1.6,
            "last_seen": now,
            "timestamp": now
        },
        {
            "type": "variation",
            "sequence": ["scan", "plan", "test"],
            "signature": "variation::scan->plan->test",
            "count": 1,
            "weight": 2.1,
            "last_seen": now,
            "timestamp": now
        },
        {
            "type": "variation",
            "sequence": ["reflect", "branch", "execute"],
            "signature": "variation::reflect->branch->execute",
            "count": 1,
            "weight": 1.7,
            "last_seen": now,
            "timestamp": now
        }
    ]
}

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("CONFLICT SEED READY")
