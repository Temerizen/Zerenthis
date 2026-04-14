import subprocess, time, sys

while True:
    subprocess.run([sys.executable, "backend/regime_engine_live.py"])
    time.sleep(60)
