import os
from datetime import datetime

def run_money():
    print("💰 Money engine running...")

    os.makedirs("backend/outputs", exist_ok=True)

    filename = f"backend/outputs/product_{int(datetime.now().timestamp())}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("Zerenthis Auto Product\n")
        f.write("Title: Viral TikTok Growth Blueprint\n")
        f.write("Price: $19\n")
        f.write("Content:\n")
        f.write("- 10 viral hooks\n- 5 scripts\n- posting strategy\n")

    print("💸 Product generated:", filename)
