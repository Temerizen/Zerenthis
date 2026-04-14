import json
import time
import requests

URL = "http://127.0.0.1:8000/api/founder/market/run"
HEADERS = {"x-api-key": "ZERENTHIS_FOUNDER_KEY"}

for i in range(12):
    print(f"\n=== PROFIT LOOP {i+1} ===")
    try:
        r = requests.post(URL, headers=HEADERS, timeout=30)
        try:
            data = r.json()
        except Exception:
            print("NON-JSON RESPONSE:")
            print(r.text)
            time.sleep(1)
            continue

        if not isinstance(data, dict):
            print("UNEXPECTED RESPONSE TYPE:")
            print(data)
            time.sleep(1)
            continue

        if "status" not in data and "detail" in data:
            print("API ERROR:")
            print(json.dumps(data, indent=2))
            time.sleep(1)
            continue

        trades = data.get("trades", []) or []
        loop_pnl = round(sum(float(t.get("pnl", 0) or 0) for t in trades if isinstance(t, dict)), 4)

        out = {
            "status": data.get("status"),
            "best_strategy": data.get("best_strategy"),
            "loop_pnl": loop_pnl,
            "trades_this_loop": len(trades),
            "balance": data.get("portfolio", {}).get("balance"),
            "account_pnl_percent": data.get("score", {}).get("pnl_percent")
        }
        print(json.dumps(out, indent=2))

    except Exception as e:
        print("REQUEST ERROR:", str(e))

    time.sleep(1)
