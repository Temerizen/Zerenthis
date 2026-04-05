import os
from datetime import datetime, timezone

OUTPUT_DIR = os.path.join("backend", "outputs", "money")

def run_money(cid):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    now = datetime.now(timezone.utc)
    filename = f"{int(now.timestamp())}.txt"
    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Generated at {now.isoformat()}")

    print(f"[MONEY][{cid}] generated {filename}", flush=True)
