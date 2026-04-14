import json
import time
import requests
from pathlib import Path

URL = "http://127.0.0.1:8000/api/founder/market/run"
HEADERS = {"x-api-key": "ZERENTHIS_FOUNDER_KEY"}

ACCOUNT_PATH = Path("backend/data/paper_account.json")
CONTROL_PATH = Path("backend/data/loop_controller_state.json")

def load_account():
    if not ACCOUNT_PATH.exists():
        return {"balance": 50.0, "wins": 0, "losses": 0, "trades": 0, "last_pnl": 0.0}
    return json.loads(ACCOUNT_PATH.read_text(encoding="utf-8-sig"))

def save_control(state):
    CONTROL_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")

start = load_account()
start_balance = float(start.get("balance", 50.0))
start_wins = int(start.get("wins", 0))
start_losses = int(start.get("losses", 0))
start_trades = int(start.get("trades", 0))

max_loops = 20
min_balance_floor = start_balance - 0.02
max_new_losses = 4
max_flat_loops = 8

flat_loops = 0
results = []

print(f"START BALANCE: {start_balance}")
print(f"STOP FLOOR: {min_balance_floor}")

for i in range(1, max_loops + 1):
    print(f"\\n=== CONTROLLED LOOP {i}/{max_loops} ===")

    try:
        r = requests.post(URL, headers=HEADERS, timeout=30)
        data = r.json()
    except Exception as e:
        print("REQUEST ERROR:", str(e))
        break

    if not isinstance(data, dict):
        print("BAD RESPONSE:", data)
        break

    if "detail" in data and "status" not in data:
        print("API ERROR:", json.dumps(data, indent=2))
        break

    trades = data.get("trades", []) or []
    loop_pnl = round(sum(float(t.get("pnl", 0) or 0) for t in trades if isinstance(t, dict)), 4)
    balance = data.get("portfolio", {}).get("balance")
    best_strategy = data.get("best_strategy")

    if loop_pnl == 0:
        flat_loops += 1
    else:
        flat_loops = 0

    acct = load_account()
    current_balance = float(acct.get("balance", start_balance))
    current_wins = int(acct.get("wins", start_wins))
    current_losses = int(acct.get("losses", start_losses))
    current_trades = int(acct.get("trades", start_trades))

    new_losses = current_losses - start_losses
    new_wins = current_wins - start_wins

    row = {
        "loop": i,
        "status": data.get("status"),
        "best_strategy": best_strategy,
        "loop_pnl": loop_pnl,
        "trades_this_loop": len(trades),
        "balance": current_balance,
        "new_wins": new_wins,
        "new_losses": new_losses,
        "flat_loops": flat_loops
    }
    results.append(row)
    print(json.dumps(row, indent=2))

    if current_balance < min_balance_floor:
        print("\\nSTOP: balance floor breached")
        break

    if new_losses >= max_new_losses:
        print("\\nSTOP: too many new losses")
        break

    if flat_loops >= max_flat_loops:
        print("\\nSTOP: too many flat loops in a row")
        break

    time.sleep(0.6)

final_acct = load_account()
summary = {
    "start_balance": start_balance,
    "end_balance": float(final_acct.get("balance", start_balance)),
    "net_change": round(float(final_acct.get("balance", start_balance)) - start_balance, 4),
    "start_wins": start_wins,
    "end_wins": int(final_acct.get("wins", start_wins)),
    "start_losses": start_losses,
    "end_losses": int(final_acct.get("losses", start_losses)),
    "start_trades": start_trades,
    "end_trades": int(final_acct.get("trades", start_trades)),
    "loops_ran": len(results),
    "last_result": results[-1] if results else None
}

save_control({
    "summary": summary,
    "results": results,
    "rules": {
        "max_loops": max_loops,
        "min_balance_floor": min_balance_floor,
        "max_new_losses": max_new_losses,
        "max_flat_loops": max_flat_loops
    }
})

print("\\n=== CONTROLLER SUMMARY ===")
print(json.dumps(summary, indent=2))
print("\\nSaved: backend/data/loop_controller_state.json")
