from backend.app.engines.money_engine import run_money
from backend.app.engines.research_engine import run_research

def run_command(command: str):
    command = command.lower()

    if command == "money":
        return run_money("manual")

    if command == "research":
        return run_research("AI business monetization")

    return {"status": "unknown_command"}

