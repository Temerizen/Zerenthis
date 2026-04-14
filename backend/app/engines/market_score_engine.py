from backend.app.engines.market_portfolio_engine import load_portfolio

def score_trades(trades):
    total = round(sum(float(t.get("pnl", t.get("profit", 0))) for t in trades), 2)
    wins = len([t for t in trades if float(t.get("pnl", t.get("profit", 0))) > 0])
    losses = len([t for t in trades if float(t.get("pnl", t.get("profit", 0))) < 0])
    portfolio = load_portfolio()

    starting_balance = float(portfolio.get("starting_balance", 50.0))
    balance = float(portfolio.get("balance", starting_balance))
    pnl_pct = 0.0 if starting_balance == 0 else round(((balance - starting_balance) / starting_balance) * 100, 2)

    return {
        "total_profit": total,
        "wins": wins,
        "losses": losses,
        "trades": len(trades),
        "starting_balance": round(starting_balance, 2),
        "ending_balance": round(balance, 2),
        "pnl_percent": pnl_pct
    }


