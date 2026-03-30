import json
import time
from pathlib import Path

DATA_FILE = Path(__file__).parent / "proposals.json"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "outputs"

def load():
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text())

def save(data):
    DATA_FILE.write_text(json.dumps(data, indent=2))

def create_proposal(data):
    items = load()

    pid = f"prop_{int(time.time()*1000)}"

    proposal = {
        "id": pid,
        "title": data.get("title",""),
        "description": data.get("description",""),
        "tier": data.get("tier","low"),
        "approved": False,
        "executed": False,
        "created_at": time.time()
    }

    items.append(proposal)
    save(items)
    return proposal

def propose(data):
    return create_proposal(data)

def pending():
    return [p for p in load() if not p.get("executed")]

def approve(pid):
    items = load()
    for p in items:
        if p["id"] == pid:
            p["approved"] = True
    save(items)

def execute(pid):
    items = load()

    for p in items:
        if p["id"] == pid and p.get("approved"):

            title = p.get("title","").lower()

            # 🔥 REAL EFFECTS
            if "weak output" in title:
                for f in OUTPUT_DIR.glob("*.pdf"):
                    with open(f, "a", encoding="utf-8") as file:
                        file.write("\n\n--- IMPROVED VERSION ---\n")
                        file.write("This product has been upgraded with stronger monetization, clearer structure, and better engagement.\n")

            if "conversion" in title or "cta" in title:
                for f in OUTPUT_DIR.glob("*.pdf"):
                    with open(f, "a", encoding="utf-8") as file:
                        file.write("\n\n--- CALL TO ACTION ---\nBuy now. Limited offer. Take action immediately.\n")

            if "monetization" in title:
                for f in OUTPUT_DIR.glob("*.pdf"):
                    with open(f, "a", encoding="utf-8") as file:
                        file.write("\n\n--- MONETIZATION SECTION ---\nPremium tier: $49\nBundle offer available.\n")

            p["executed"] = True
            save(items)

            return {"ok": True, "effect": "applied"}

    return {"error": "not approved"}
