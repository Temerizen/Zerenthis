import time, json, requests, traceback
from pathlib import Path

from backend.architect import build_plan, complete_module
from backend.critic import evaluate

PLAN_PATH = Path("backend/data/autopilot/architect_plan.json")

BASE_URL = "https://zerenthis-production.up.railway.app"

def loop():
    while True:
        try:
            print("=== ARCHITECT THINKING ===")
            plan = build_plan()
            print(plan)

            if plan.get("status") == "complete":
                print("ROADMAP COMPLETE")
                time.sleep(300)
                continue

            module = plan["module"]

            print("=== BUILDER EXECUTION ===")

            response = requests.post(
                f"{BASE_URL}/api/product-pack",
                json={
                    "topic": module,
                    "niche": "AI System",
                    "tone": "Elite",
                    "buyer": "Founders",
                    "promise": "build powerful systems",
                    "bonus": "frameworks",
                    "notes": f"building module: {module}"
                },
                timeout=120
            )

            result = response.json()
            text = str(result)

            print("=== CRITIC EVALUATING ===")
            scores = evaluate(text)
            print(scores)

            if scores["overall"] >= 7:
                print("MODULE COMPLETED:", module)
                complete_module(module)

        except Exception as e:
            print("ERROR:", str(e))
            print(traceback.format_exc())

        time.sleep(60)

if __name__ == "__main__":
    loop()
