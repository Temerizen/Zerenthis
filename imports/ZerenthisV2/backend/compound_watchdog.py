import requests, time, subprocess, sys, os

ROOT = r"C:\ZerenthisV2"
PY = sys.executable
COMPOUNDER = os.path.join(ROOT, "backend", "app", "builder", "compounding_engine.py")
ACCOUNT_FILE = os.path.join(ROOT, "backend", "data", "paper_account.json")

def print_account():
    if os.path.exists(ACCOUNT_FILE):
        with open(ACCOUNT_FILE, "r", encoding="utf-8-sig") as f:
            print("[ACCOUNT]", f.read())

while True:
    subprocess.run([PY, COMPOUNDER], cwd=ROOT)
    print_account()
    time.sleep(10)
