import json

def audit():
    try:
        with open("backend/data/roadmap.json") as f:
            roadmap = json.load(f)
        return {
            "status": "ok",
            "modules": roadmap["empire"]["modules"]
        }
    except:
        return {"status": "error"}

