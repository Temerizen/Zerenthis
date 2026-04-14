import time, requests, json

BASE = "https://semantiqai-backend-production-bcab.up.railway.app"

def run_loop():
    while True:
        try:
            print("\n=== EVOLUTION LOOP START ===")

            evo = requests.post(f"{BASE}/api/evolution/run").json()
            print("Evolution:", evo.get("pattern"))

            jobs = evo.get("jobs_created", [])

            for j in jobs:
                res = requests.post(f"{BASE}/api/product-pack", json=j).json()
                print("Generated:", res.get("job_id"))

                time.sleep(2)

            print("Running ascension...")
            asc = requests.post(f"{BASE}/api/ascension/backfill").json()
            print("Ascension:", asc)

            print("=== LOOP COMPLETE | sleeping 60s ===")
            time.sleep(60)

        except Exception as e:
            print("ERROR:", str(e))
            time.sleep(10)

if __name__ == "__main__":
    run_loop()
