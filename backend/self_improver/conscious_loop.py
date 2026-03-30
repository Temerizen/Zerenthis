import json, time, uuid
from pathlib import Path

ROOT = Path(r"C:\Zerenthis")
STATE_FILE = ROOT / "backend/data/self_improver/state.json"
MEMORY_FILE = ROOT / "backend/data/self_improver/memory.json"
LOG_FILE = ROOT / "backend/data/self_improver/reflections.json"

STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

def load(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except:
            return default
    return default

def save(path, data):
    path.write_text(json.dumps(data, indent=2))

state = load(STATE_FILE, {
    "cycles": 0,
    "last_health": {},
    "goals": ["increase output quality", "increase monetization", "reduce failures"]
})

memory = load(MEMORY_FILE, {
    "successful_patterns": [],
    "failed_patterns": [],
})

def reflect():
    state["cycles"] += 1

    reflection = {
        "id": str(uuid.uuid4()),
        "cycle": state["cycles"],
        "timestamp": time.time(),
        "analysis": []
    }

    # Evaluate system signals
    outputs = list((ROOT / "backend/data/outputs").glob("*"))
    proposals = load(ROOT / "backend/data/self_improver/proposals.json", [])

    reflection["analysis"].append(f"Total outputs: {len(outputs)}")
    reflection["analysis"].append(f"Total proposals: {len(proposals)}")

    # Basic intelligence layer
    if len(outputs) < 3:
        reflection["analysis"].append("Low output production detected ? prioritize generation")
        memory["failed_patterns"].append("low_output")

    if len(proposals) > 10:
        reflection["analysis"].append("Too many proposals ? risk of clutter")
    
    if any(p.get("status") == "failed" for p in proposals):
        reflection["analysis"].append("Failures detected ? tighten validation")

    # Learn patterns
    if len(outputs) > 5:
        memory["successful_patterns"].append("consistent_generation")

    # Store reflection
    logs = load(LOG_FILE, [])
    logs.append(reflection)

    save(LOG_FILE, logs[-50:])  # keep last 50
    save(MEMORY_FILE, memory)
    save(STATE_FILE, state)

    print("Reflection complete:", reflection["analysis"])

if __name__ == "__main__":
    while True:
        reflect()
        time.sleep(90)
