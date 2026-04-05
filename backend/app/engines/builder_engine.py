from datetime import datetime, timezone
import json, os

DATA_DIR = os.path.join("backend", "data")

def run_builder(cid):
    idea = f"Idea generated at {datetime.now(timezone.utc).isoformat()}"
    print(f"[BUILDER][{cid}] {idea}", flush=True)
