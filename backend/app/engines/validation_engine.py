from pathlib import Path
import json

FILE = Path("backend/data/market/validation.json")

def load_validation():
    if not FILE.exists():
        return {"runs": []}
    return json.loads(FILE.read_text())

def save_validation(data):
    FILE.parent.mkdir(parents=True, exist_ok=True)
    FILE.write_text(json.dumps(data, indent=2))

def record_run(result):
    data = load_validation()
    data["runs"].append(result)
    save_validation(data)

def reliability_score():
    data = load_validation()
    runs = data["runs"][-20:]

    if not runs:
        return 0

    profits = [r.get("profit", 0) for r in runs]
    balances = [r.get("balance", 0) for r in runs]
    drawdowns = [r.get("drawdown", 0) for r in runs]

    avg_profit = sum(profits) / len(profits)
    max_dd = max(drawdowns) if drawdowns else 0
    consistency = sum(1 for p in profits if p > 0) / len(profits)

    score = (avg_profit * 50) + (consistency * 40) - (max_dd * 100)

    return round(score, 2)

