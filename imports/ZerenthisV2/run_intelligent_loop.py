import time
import requests

BASE = "http://127.0.0.1:8000"

for i in range(100):
    print(f"\n=== INTELLIGENT LOOP {i+1} ===")

    try:
        r = requests.post(f"{BASE}/api/founder/market/run", headers={"x-api-key":"ZERENTHIS_FOUNDER_KEY"})
        print(r.json())
    except Exception as e:
        print("market error:", e)

    try:
        from backend.app.engines.intelligence_engine import run_intelligence
        result = run_intelligence()
        print("brain:", result)
    except Exception as e:
        print("brain error:", e)

    time.sleep(1)
