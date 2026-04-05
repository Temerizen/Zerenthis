from datetime import datetime, timezone

def run_builder(cid):
    now = datetime.now(timezone.utc).isoformat()
    print(f"[BUILDER][{cid}] idea generated at {now}", flush=True)
