from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILE = ROOT / "backend" / "data" / "self_improver" / "proposals.json"
BACKUP = ROOT / "backend" / "data" / "self_improver" / "proposals.pre_dedupe.json"

def main():
    if not FILE.exists():
        print("No proposals.json found")
        return

    data = json.loads(FILE.read_text(encoding="utf-8"))
    BACKUP.write_text(json.dumps(data, indent=2), encoding="utf-8")

    latest_by_id = {}
    for item in data:
        pid = item.get("id")
        if not pid:
            continue
        ts = float(item.get("created_ts", 0) or 0)
        existing = latest_by_id.get(pid)
        if existing is None or ts >= float(existing.get("created_ts", 0) or 0):
            latest_by_id[pid] = item

    cleaned = list(latest_by_id.values())
    cleaned.sort(key=lambda x: float(x.get("created_ts", 0) or 0))

    FILE.write_text(json.dumps(cleaned, indent=2), encoding="utf-8")
    print(f"Backed up to: {BACKUP}")
    print(f"Original count: {len(data)}")
    print(f"Cleaned count: {len(cleaned)}")
    print(f"Removed duplicates: {len(data) - len(cleaned)}")

if __name__ == "__main__":
    main()
