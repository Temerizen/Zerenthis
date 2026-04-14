import subprocess, time, sys, os

ROOT = r"C:\ZerenthisV2"
PY = sys.executable
CTRL = os.path.join(ROOT, "backend", "app", "builder", "control_engine.py")
STATE = os.path.join(ROOT, "backend", "data", "control_state.json")

def show():
    if os.path.exists(STATE):
        with open(STATE, "r", encoding="utf-8-sig") as f:
            print("[CONTROL STATE]", f.read())

while True:
    subprocess.run([PY, CTRL], cwd=ROOT)
    show()
    time.sleep(5)
