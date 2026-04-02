import time
from pathlib import Path

from self_improver.level2 import run_performance_cycle

LOG_FILE = Path("backend/data/self_improver/autopilot_log.txt")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

SLEEP_SECONDS = 300  # 5 minutes


def write_log(message: str):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def run_once():
    write_log("AUTOPILOT cycle starting")
    try:
        result = run_performance_cycle()
        write_log(f"AUTOPILOT result: {result}")
        return {"ok": True, "result": result}
    except Exception as e:
        write_log(f"AUTOPILOT error: {e}")
        return {"ok": False, "error": str(e)}


def main():
    write_log("AUTOPILOT ONLINE")
    while True:
        run_once()
        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()
