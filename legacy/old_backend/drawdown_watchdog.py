import subprocess, time, sys, os

ROOT = r"C:\ZerenthisV2"
PY = sys.executable
SHIELD = os.path.join(ROOT, "backend", "app", "builder", "drawdown_shield.py")
ACCOUNT = os.path.join(ROOT, "backend", "data", "paper_account.json")
PARAMS = os.path.join(ROOT, "backend", "data", "market_params.json")
STATE = os.path.join(ROOT, "backend", "data", "risk_state.json")

def show(path, label):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8-sig") as f:
            print(f"[{label}] {f.read()}")

while True:
    subprocess.run([PY, SHIELD], cwd=ROOT)
    show(ACCOUNT, "ACCOUNT")
    show(PARAMS, "PARAMS")
    show(STATE, "RISK_STATE")
    time.sleep(5)
