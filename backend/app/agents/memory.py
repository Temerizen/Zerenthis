import os, json

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory.json")

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)

def get_user_memory(uid):
    mem = load_memory()
    return mem.get(str(uid), {})

def update_user_memory(uid, key, value):
    mem = load_memory()
    uid = str(uid)
    if uid not in mem:
        mem[uid] = {}
    mem[uid][key] = value
    save_memory(mem)

