import time, json
from pathlib import Path

from backend.director_core import main as director_run
from backend.critic import evaluate

PLAN_PATH = Path("backend/data/autopilot/director_plan.json")

def loop():
    while True:
        print("=== DIRECTOR THINKING ===")
        director_run()

        if PLAN_PATH.exists():
            plan = json.load(open(PLAN_PATH))
            text = str(plan)

            print("=== CRITIC EVALUATING ===")
            scores = evaluate(text)
            print(scores)

        time.sleep(30)

if __name__ == "__main__":
    loop()
