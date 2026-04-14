import time
import requests

BASE = "http://127.0.0.1:8000"
def loop():
    while True:
        try:
            r = requests.post(f"{BASE}/api/worker/run", timeout=30)
            print("Worker:", r.status_code)
        except Exception as e:
            print("Loop error:", e)

        time.sleep(5)

if __name__ == "__main__":
    loop()






