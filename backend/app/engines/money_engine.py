import glob
import json
import os
from datetime import datetime, timezone

DATA_DIR = os.path.join("backend", "data")
OUTPUT_DIR = os.path.join("backend", "outputs")
LATEST_IDEA_PATH = os.path.join(DATA_DIR, "latest_builder_idea.json")
MONEY_STATE_PATH = os.path.join(DATA_DIR, "money_engine_state.json")

def _utc_now():
    return datetime.now(timezone.utc).isoformat()

def _prune_old_money_files(max_keep=40):
    pattern = os.path.join(OUTPUT_DIR, "money_offer_*.txt")
    files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)

    for path in files[max_keep:]:
        try:
            os.remove(path)
            print(f"[MONEY {_utc_now()}] pruned old file: {os.path.basename(path)}", flush=True)
        except Exception as e:
            print(f"[MONEY {_utc_now()}] prune failed for {os.path.basename(path)}: {e}", flush=True)

def run_money():
    now = _utc_now()
    print(f"[MONEY {now}] money engine running", flush=True)

    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if os.path.exists(LATEST_IDEA_PATH):
        with open(LATEST_IDEA_PATH, "r", encoding="utf-8") as f:
            idea = json.load(f)
    else:
        idea = {
            "title": "Starter Offer",
            "niche": "General",
            "buyer": "General audience",
            "promise": "Get started quickly",
            "offer": "$19 starter bundle"
        }

    filename = f"money_offer_{int(datetime.now(timezone.utc).timestamp())}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("Zerenthis Money Output\n")
        f.write(f"Created: {now}\n")
        f.write(f"Title: {idea.get('title', 'Starter Offer')}\n")
        f.write(f"Niche: {idea.get('niche', 'General')}\n")
        f.write(f"Buyer: {idea.get('buyer', 'General audience')}\n")
        f.write(f"Promise: {idea.get('promise', 'Useful result')}\n")
        f.write(f"Offer: {idea.get('offer', '$19 starter bundle')}\n")

    with open(MONEY_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "last_run_at": now,
            "last_file_name": filename,
            "last_title": idea.get("title", "Starter Offer")
        }, f, indent=2)

    print(f"[MONEY {now}] product generated: {filepath}", flush=True)
    _prune_old_money_files(max_keep=40)
