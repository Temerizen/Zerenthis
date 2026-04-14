def should_lock(strategy_data):
    runs = strategy_data.get("runs",0)
    winrate = strategy_data.get("avg_winrate",0)
    return runs >= 5 and winrate >= 70
