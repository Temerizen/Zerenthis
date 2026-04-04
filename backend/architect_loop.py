import json, time, traceback
from pathlib import Path
from datetime import datetime
from backend.proposal_engine import build_proposal

BASE = Path(__file__).resolve().parents[1]
AUTO = BASE / "backend" / "data" / "autopilot"
RUNS = AUTO / "architect_runs.json"

def now():
    return datetime.utcnow().isoformat()

def read_json(path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return default

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def append_run(entry):
    data = read_json(RUNS, [])
    if not isinstance(data, list):
        data = []
    data.append(entry)
    write_json(RUNS, data[-200:])

def loop():
    while True:
        try:
            proposal = build_proposal()
            print("=== ARCHITECT PROPOSAL ===")
            print(json.dumps(proposal, indent=2))

            append_run({
                "time": now(),
                "proposal": proposal
            })

        except Exception as e:
            err = {
                "time": now(),
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print("=== ARCHITECT ERROR ===")
            print(json.dumps(err, indent=2))
            append_run(err)

        time.sleep(300)

if __name__ == "__main__":
    loop()
