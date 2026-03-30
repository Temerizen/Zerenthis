import time
import sys
from pathlib import Path

# Ensure backend is root for imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from self_improver.worker import run_ai_cycle
from self_improver.engine import pending, approve, execute

print("🧠 Zerenthis Autopilot ONLINE")

SAFE_KEYWORDS = [
    "quality",
    "metadata",
    "health",
    "validation",
    "monetization",
    "output",
    "scoring"
]

def auto_loop():
    while True:
        try:
            print("\n--- AI THINKING ---")
            run_ai_cycle()

            props = pending()
            print(f"Found {len(props)} proposals")

            for p in props:
                title = str(p.get("title","")).lower()
                pid = p.get("id")

                if any(k in title for k in SAFE_KEYWORDS):
                    print("✅ Auto-approving:", title)
                    approve(pid)
                    result = execute(pid)
                    print("⚙️ Result:", result)
                else:
                    print("🟡 Skipped:", title)

        except Exception as e:
            print("❌ AUTOPILOT ERROR:", e)

        print("💤 Sleeping 120s...")
        time.sleep(120)

if __name__ == "__main__":
    auto_loop()
