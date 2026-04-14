import os
import sys
import json
import time
import requests

BASE = os.getenv("SEMANTIQAI_BASE_URL", "http://127.0.0.1:5000")

def check(name, method, path, expected=(200,), **kwargs):
    url = BASE + path
    try:
        r = requests.request(method, url, timeout=10, **kwargs)
        ok = r.status_code in expected
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {r.status_code} {path}")
        if not ok:
            print(r.text[:500])
        return ok
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return False

def main():
    results = []
    results.append(check("health", "GET", "/health"))
    results.append(check("ready", "GET", "/ready"))
    results.append(check("public site", "GET", "/public/site"))
    print("")
    print("Smoke summary:", f"{sum(1 for x in results if x)}/{len(results)} passed")
    sys.exit(0 if all(results) else 1)

if __name__ == "__main__":
    main()

