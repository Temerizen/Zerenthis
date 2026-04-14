import requests, time, subprocess, sys, os

ROOT = r"C:\ZerenthisV2"
PY = sys.executable
ENFORCER = os.path.join(ROOT, "backend", "app", "builder", "live_param_enforcer.py")
ACCOUNT_FILE = os.path.join(ROOT, "backend", "data", "paper_account.json")
PARAMS_FILE = os.path.join(ROOT, "backend", "data", "market_params.json")

def show(path, label):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8-sig") as f:
            print(f"[{label}] {f.read()}")

while True:
    subprocess.run([PY, ENFORCER], cwd=ROOT)
    show(ACCOUNT_FILE, "ACCOUNT")
    show(PARAMS_FILE, "PARAMS")
    time.sleep(5)
