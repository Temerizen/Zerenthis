from pathlib import Path
import json
import shutil

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"

OUTPUT_DIR = DATA_DIR / "outputs"
AUTO_DIR = DATA_DIR / "autopilot"
TOP_DIR = DATA_DIR / "top_performers"

WINNERS_FILE = AUTO_DIR / "winners.json"

def read_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except:
        pass
    return default

def main():
    winners = read_json(WINNERS_FILE, [])

    if not isinstance(winners, list):
        print("No winners found")
        return

    count = 0

    for w in winners:
        fname = w.get("file_name")
        if not fname:
            continue

        src = OUTPUT_DIR / fname
        dst = TOP_DIR / fname

        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
            count += 1

    print(f"Backfilled {count} top performers")

if __name__ == "__main__":
    main()
