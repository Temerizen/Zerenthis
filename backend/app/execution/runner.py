import os, importlib.util, traceback, time, json

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
GEN_DIR = os.path.join(BASE_DIR, "generated")
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
LOG_PATH = os.path.join(DATA_DIR, "execution_log.json")

os.makedirs(DATA_DIR, exist_ok=True)

def load_log():
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, "r") as f:
        return json.load(f)

def save_log(data):
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def score_result(result):
    if result is None:
        return 0
    if isinstance(result, dict):
        return len(result.keys()) * 2
    if isinstance(result, str):
        return min(len(result) // 50, 10)
    return 1

def run_system(path):
    name = os.path.basename(path).replace(".py","")
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "run"):
            result = module.run()
        else:
            return {"status":"skipped","reason":"no run()"}, 0

        score = score_result(result)
        return {"status":"success","result":str(result)}, score

    except Exception as e:
        return {"status":"error","error":str(e), "trace": traceback.format_exc()}, 0

def execute_all(limit=10):
    files = sorted([f for f in os.listdir(GEN_DIR) if f.endswith(".py")], reverse=True)
    log = load_log()

    results = []

    for f in files[:limit]:
        path = os.path.join(GEN_DIR, f)
        res, score = run_system(path)

        entry = {
            "file": f,
            "result": res,
            "score": score,
            "time": time.time()
        }

        log.insert(0, entry)
        results.append(entry)

    save_log(log[:1000])
    return results

if __name__ == "__main__":
    out = execute_all()
    print(json.dumps(out, indent=2))
