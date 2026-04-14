import json
import os

ACCOUNT_FILE = os.path.join("backend", "data", "paper_account.json")
PORTFOLIO_FILE = os.path.join("backend", "data", "portfolio.json")

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_portfolio():
    account = load_json(ACCOUNT_FILE, {"balance": 50.0})

    portfolio = load_json(PORTFOLIO_FILE, {
        "starting_balance": 50.0,
        "balance": float(account.get("balance", 50.0)),
        "risk_per_trade": 0.1,
        "max_open_positions": 3,
        "last_run_trades": [],
        "equity_curve": [],
        "peak_balance": float(account.get("balance", 50.0))
    })

    real_balance = float(account.get("balance", 50.0))
    portfolio["balance"] = real_balance

    equity_curve = portfolio.get("equity_curve", [])
    if not isinstance(equity_curve, list):
        equity_curve = []

    equity_curve.append(real_balance)
    portfolio["equity_curve"] = equity_curve
    portfolio["peak_balance"] = max(float(portfolio.get("peak_balance", real_balance)), real_balance)

    save_json(PORTFOLIO_FILE, portfolio)
    return portfolio

def save_portfolio(portfolio):
    save_json(PORTFOLIO_FILE, portfolio)

def reset_portfolio(starting_balance=50.0, risk_per_trade=0.1):
    starting_balance = float(starting_balance)
    risk_per_trade = float(risk_per_trade)

    portfolio = {
        "starting_balance": starting_balance,
        "balance": starting_balance,
        "risk_per_trade": risk_per_trade,
        "max_open_positions": 3,
        "last_run_trades": [],
        "equity_curve": [starting_balance],
        "peak_balance": starting_balance
    }

    account = {
        "balance": starting_balance,
        "wins": 0,
        "losses": 0,
        "trades": 0,
        "last_pnl": 0.0
    }

    save_json(PORTFOLIO_FILE, portfolio)
    save_json(ACCOUNT_FILE, account)

    return portfolio
