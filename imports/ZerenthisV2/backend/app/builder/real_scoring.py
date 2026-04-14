from backend.app.builder.performance_memory import record_run

def compute_real_score(pnl, balance):
    if balance <= 0:
        return -100

    growth = pnl / balance

    if pnl > 0:
        return 10 + growth * 100
    else:
        return -10 + growth * 100

def override_score(res, trade):
    pnl = trade["pnl"]
    balance = trade["balance_after"]

    real_score = compute_real_score(pnl, balance)

    record_run(res["params"], real_score)

    return real_score
