import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from self_improver.worker import run_ai_cycle
from self_improver.engine import pending, approve, execute

print("🚀 Zerenthis EVOLUTION ENGINE ONLINE")

SAFE = [
    "quality",
    "monetization",
    "pricing",
    "upsell",
    "metadata",
    "output",
    "scoring",
    "health",
    "validation",
    "conversion",
    "cta",
    "offer"
]

def evolve():
    while True:
        try:
            print("\n🧠 Generating intelligence...")
            run_ai_cycle()

            props = pending()
            print(f"📦 Proposals: {len(props)}")

            for p in props:
                title = str(p.get("title","")).lower()
                pid = p.get("id")

                # aggressive but safe filtering
                if any(k in title for k in SAFE):
                    print("🔥 APPLYING:", title)
                    approve(pid)
                    result = execute(pid)
                    print("⚙️ RESULT:", result)
                else:
                    print("⏸ HOLD:", title)

        except Exception as e:
            print("❌ ERROR:", e)

        print("💤 Looping in 90s...")
        time.sleep(90)

if __name__ == "__main__":
    evolve()
