import json, uuid, os

QUEUE_FILE = "backend/self_improve/queue.json"

def load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    return json.load(open(QUEUE_FILE))

def save_queue(q):
    json.dump(q, open(QUEUE_FILE, "w"), indent=2)

def add_patch(patch):
    q = load_queue()
    patch["id"] = str(uuid.uuid4())
    patch["status"] = "pending"
    q.append(patch)
    save_queue(q)
    return patch["id"]

def get_pending():
    return [p for p in load_queue() if p["status"] == "pending"]
