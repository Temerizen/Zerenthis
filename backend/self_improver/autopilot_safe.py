import time
from backend.self_improver.worker import run_ai_cycle
from backend.self_improver.engine import pending, approve, execute

print("🧠 Zerenthis Autopilot ONLINE")

def auto_loop():
    while True:
        print("\n--- AI THINKING ---")
        run_ai_cycle()

        props = pending()
        print(f"Found {len(props)} proposals")

        for p in props:
            title = p.get("title","")
            pid = p.get("id")

            # 🧠 SAFE AUTO-APPROVAL RULES
            safe_keywords = [
                "quality",
                "metadata",
                "health",
                "validation",
                "monetization",
                "output",
                "scoring"
            ]

            if any(k in title.lower() for k in safe_keywords):
                print("✅ Auto-approving:", title)
                approve(pid)
                result = execute(pid)
                print("⚙️ Result:", result)
            else:
                print("🟡 Skipped (needs human):", title)

        print("💤 Sleeping 2 minutes...")
        time.sleep(120)

if __name__ == "__main__":
    auto_loop()
