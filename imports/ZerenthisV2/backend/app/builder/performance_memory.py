import json, os, time

FILE = "backend/data/performance_memory.json"

def load():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save(data):
    os.makedirs("backend/data", exist_ok=True)
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data[-200:], f, indent=2)

def record_run(params, score):
    mem = load()
    mem.append({
        "time": time.time(),
        "params": params,
        "score": score
    })
    save(mem)

def get_best():
    mem = load()
    if not mem:
        return None
    return max(mem, key=lambda x: x["score"])

def get_elite():
    mem = load()
    if not mem:
        return None

    buckets = {}
    for m in mem:
        key = str({k: round(v, 2) for k, v in m["params"].items()})
        buckets.setdefault(key, []).append(m["score"])

    ranked = []
    for k, scores in buckets.items():
        avg = sum(scores) / len(scores)
        stability = len(scores)
        ranked.append((avg * (1 + stability * 0.1), k))

    best_key = max(ranked, key=lambda x: x[0])[1]
    return eval(best_key)
