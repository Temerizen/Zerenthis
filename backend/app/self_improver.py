import os
import json
from datetime import datetime

DATA_DIR = "backend/data"
PROPOSALS_FILE = os.path.join(DATA_DIR, "proposals.json")

os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def propose_change():
    proposals = load_json(PROPOSALS_FILE, [])

    proposal = {
        "id": len(proposals) + 1,
        "idea": "Improve hook generation quality",
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }

    proposals.append(proposal)
    save_json(PROPOSALS_FILE, proposals)

    return proposal

def approve_proposal(pid):
    proposals = load_json(PROPOSALS_FILE, [])

    for p in proposals:
        if p["id"] == pid:
            p["status"] = "approved"

    save_json(PROPOSALS_FILE, proposals)
    return {"approved": pid}

