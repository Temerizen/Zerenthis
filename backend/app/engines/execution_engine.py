import time, json, os

OUT = "backend/outputs"

def run_task(idea):
    os.makedirs(OUT, exist_ok=True)

    result = {
        "idea": idea,
        "product": f"{idea} Product",
        "content": f"{idea} viral script",
        "status": "executed"
    }

    fname = idea.replace(" ", "_") + ".json"
    path = os.path.join(OUT, fname)

    with open(path, "w") as f:
        json.dump(result, f, indent=2)

    return result
