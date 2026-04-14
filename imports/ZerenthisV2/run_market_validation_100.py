import json
import time
import requests
from statistics import mean

URL = "http://127.0.0.1:8000/api/founder/market/run"
HEADERS = {"x-api-key": "ZERENTHIS_FOUNDER_KEY"}

loops = 100
loop_pnls = []
balances = []
trade_counts = []
wins = 0
losses = 0
errors = 0

for i in range(loops):
    print(f"\n=== VALIDATION LOOP {i+1}/{loops} ===")
    try:
        r = requests.post(URL, headers=HEADERS, timeout=30)
        data = r.json()

        if not isinstance(data, dict):
            errors += 1
            print("BAD RESPONSE:", data)
            time.sleep(0.5)
            continue

        if "detail" in data and "status" not in data:
            errors += 1
            print("API ERROR:")
            print(json.dumps(data, indent=2))
            time.sleep(0.5)
            continue

        trades = data.get("trades", []) or []
        loop_pnl = round(sum(float(t.get("pnl", 0) or 0) for t in trades if isinstance(t, dict)), 4)
        balance = data.get("portfolio", {}).get("balance")
        best_strategy = data.get("best_strategy")

        loop_pnls.append(loop_pnl)
        trade_counts.append(len(trades))

        if balance is not None:
            try:
                balances.append(float(balance))
            except Exception:
                pass

        if loop_pnl > 0:
            wins += 1
        elif loop_pnl < 0:
            losses += 1

        rolling = loop_pnls[-20:] if len(loop_pnls) >= 20 else loop_pnls[:]
        rolling_expectancy = round(mean(rolling), 6) if rolling else 0.0

        out = {
            "status": data.get("status"),
            "best_strategy": best_strategy,
            "loop_pnl": loop_pnl,
            "trades_this_loop": len(trades),
            "balance": balance,
            "rolling_20_expectancy": rolling_expectancy
        }
        print(json.dumps(out, indent=2))

        time.sleep(0.5)

    except Exception as e:
        errors += 1
        print("REQUEST ERROR:", str(e))
        time.sleep(0.5)

summary = {
    "loops_requested": loops,
    "loops_completed": len(loop_pnls),
    "errors": errors,
    "positive_loops": wins,
    "negative_loops": losses,
    "flat_loops": len([x for x in loop_pnls if x == 0]),
    "avg_loop_pnl": round(mean(loop_pnls), 6) if loop_pnls else 0.0,
    "avg_trades_per_loop": round(mean(trade_counts), 4) if trade_counts else 0.0,
    "start_balance": balances[0] if balances else None,
    "end_balance": balances[-1] if balances else None,
    "net_balance_change": round((balances[-1] - balances[0]), 4) if len(balances) >= 2 else None,
    "max_balance": max(balances) if balances else None,
    "min_balance": min(balances) if balances else None,
}

with open("backend/data/market_validation_100.json", "w", encoding="utf-8") as f:
    json.dump({
        "summary": summary,
        "loop_pnls": loop_pnls,
        "balances": balances,
        "trade_counts": trade_counts
    }, f, indent=2)

print("\n=== FINAL SUMMARY ===")
print(json.dumps(summary, indent=2))
print("\nSaved: backend/data/market_validation_100.json")
