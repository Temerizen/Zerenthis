import os, random, shutil

BASE = os.path.dirname(__file__)
GEN = os.path.join(BASE, "generated")
APPROVED = os.path.join(BASE, "approved")

def mutate_content(text):
    mutations = [
        ("beginner", "advanced"),
        ("starter", "pro"),
        ("simple", "high-converting"),
        ("fast", "scalable"),
        ("product", "digital asset"),
    ]
    for a,b in mutations:
        if a in text:
            return text.replace(a,b)
    return text + " (improved version)"

def create_mutation(file):
    src = os.path.join(APPROVED, file)
    if not os.path.exists(src): return
    with open(src, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = mutate_content(content)
    new_name = "mutated_" + str(random.randint(100000,999999)) + ".py"
    with open(os.path.join(GEN, new_name), "w", encoding="utf-8") as f:
        f.write(new_content)

def run():
    approved = [f for f in os.listdir(APPROVED) if f.endswith(".py")]
    if not approved:
        return {"ok": True, "message": "no approved systems yet"}

    for f in approved[:5]:
        create_mutation(f)

    return {
        "ok": True,
        "mutations_created": len(approved[:5])
    }

