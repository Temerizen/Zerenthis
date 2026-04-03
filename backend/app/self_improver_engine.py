import os, json, uuid
from datetime import datetime

DATA_PATH = "backend/data/self_improver.json"

def _now():
    return datetime.utcnow().isoformat()+"Z"

def _load():
    if not os.path.exists(DATA_PATH):
        return {"proposals":[]}
    try:
        return json.load(open(DATA_PATH,"r",encoding="utf-8"))
    except:
        return {"proposals":[]}

def _save(data):
    json.dump(data, open(DATA_PATH,"w",encoding="utf-8"), indent=2)

def generate_proposals(history):
    proposals = []
    for item in history[:5]:
        topic = item.get("topic","")
        score = item.get("scores",{}).get("overall",5)

        proposals.append({
            "id": str(uuid.uuid4()),
            "type": "content_expansion",
            "title": f"Scale winning topic: {topic}",
            "description": f"Generate 5 more variants and push distribution",
            "priority": round(score,2),
            "status": "pending",
            "created_at": _now()
        })

        proposals.append({
            "id": str(uuid.uuid4()),
            "type": "monetization_upgrade",
            "title": f"Create product for {topic}",
            "description": "Turn this into a sellable bundle",
            "priority": round(score-1,2),
            "status": "pending",
            "created_at": _now()
        })

    return proposals

def store_proposals(new_props):
    data = _load()
    existing = data["proposals"]

    for p in new_props:
        if not any(x["title"]==p["title"] for x in existing):
            existing.append(p)

    existing = sorted(existing, key=lambda x: x["priority"], reverse=True)[:50]
    data["proposals"] = existing
    _save(data)
    return existing

def get_proposals():
    return _load()["proposals"]

def approve_proposal(pid):
    data = _load()
    for p in data["proposals"]:
        if p["id"] == pid:
            p["status"] = "approved"
    _save(data)
    return {"status":"approved"}

def execute_proposal(pid):
    data = _load()
    for p in data["proposals"]:
        if p["id"] == pid:
            if p["status"] != "approved":
                return {"error":"not approved"}

            p["status"] = "executed"
            p["executed_at"] = _now()

            # SAFE EXECUTION ONLY
            if p["type"] == "content_expansion":
                return {
                    "result":"generated expansion plan",
                    "next_step":"run body-loop with new variants"
                }

            if p["type"] == "monetization_upgrade":
                return {
                    "result":"product idea created",
                    "next_step":"generate product + landing"
                }

    _save(data)
    return {"status":"executed"}
