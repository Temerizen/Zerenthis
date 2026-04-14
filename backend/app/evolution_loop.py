import os, json, random, shutil, time

BASE = os.path.dirname(__file__)
GEN = os.path.join(BASE, "generated")
APPROVED = os.path.join(BASE, "approved")
QUAR = os.path.join(BASE, "quarantine")
DATA = os.path.join(os.path.dirname(BASE), "data")

STATE_PATH = os.path.join(DATA, "evolution_memory.json")

os.makedirs(GEN, exist_ok=True)
os.makedirs(APPROVED, exist_ok=True)
os.makedirs(QUAR, exist_ok=True)
os.makedirs(DATA, exist_ok=True)

def load_state():
    if not os.path.exists(STATE_PATH):
        return {"history": []}
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(s):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2)

def smart_score(result):
    text = str(result).lower()
    score = 0

    if len(text) > 50: score += 2
    if len(text) > 120: score += 3
    if any(k in text for k in ["title","summary","plan","offer","steps","content"]): score += 4
    if any(k in text for k in ["price","buyer","problem","solution","cta"]): score += 4
    if "alive" in text: score -= 3
    if "error" in text: score -= 5

    return max(score, 0)

def run_file(path):
    try:
        namespace = {}
        exec(open(path, encoding="utf-8").read(), namespace)
        if "run" not in namespace:
            return {"ok": False, "score": 0, "result": "no run()"}
        result = namespace["run"]()
        score = smart_score(result)
        return {"ok": True, "score": score, "result": result}
    except Exception as e:
        return {"ok": False, "score": 0, "result": str(e)}

def mutate_code(code):
    mutations = [
        ("beginner","advanced"),
        ("simple","high-converting"),
        ("starter","premium"),
        ("fast","scalable"),
        ("product","digital asset")
    ]
    for a,b in mutations:
        if a in code:
            return code.replace(a,b)
    return code + "\n# mutated variant"

def evolve():
    state = load_state()

    files = [f for f in os.listdir(GEN) if f.endswith(".py")]
    results = []

    # RUN + SCORE
    for f in files[:20]:
        path = os.path.join(GEN, f)
        res = run_file(path)
        res["file"] = f
        results.append(res)

    # SORT BEST → WORST
    results.sort(key=lambda x: x["score"], reverse=True)

    top = results[:5]
    mid = results[5:12]
    low = results[12:]

    promoted = []
    mutated = []
    quarantined = []

    # PROMOTE BEST
    for r in top:
        if r["score"] >= 5:
            src = os.path.join(GEN, r["file"])
            dst = os.path.join(APPROVED, r["file"])
            if os.path.exists(src):
                shutil.copy2(src, dst)
                promoted.append(r["file"])

    # MUTATE TOP + MID (CRITICAL CHANGE)
    for r in top + mid:
        src = os.path.join(GEN, r["file"])
        if not os.path.exists(src): continue

        code = open(src, encoding="utf-8").read()
        new_code = mutate_code(code)

        new_name = f"evo_{int(time.time()*1000)}_{random.randint(1000,9999)}.py"
        with open(os.path.join(GEN, new_name), "w", encoding="utf-8") as f:
            f.write(new_code)

        mutated.append(new_name)

    # QUARANTINE WORST
    for r in low:
        src = os.path.join(GEN, r["file"])
        if os.path.exists(src):
            shutil.move(src, os.path.join(QUAR, r["file"]))
            quarantined.append(r["file"])

    # SAVE MEMORY
    state["history"].append({
        "time": time.time(),
        "top_scores": [r["score"] for r in top],
        "mutations": len(mutated)
    })

    save_state(state)

    return {
        "ok": True,
        "promoted": promoted,
        "mutated": len(mutated),
        "quarantined": quarantined,
        "top_scores": [r["score"] for r in top]
    }

if __name__ == "__main__":
    print(json.dumps(evolve(), indent=2))

