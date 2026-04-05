from backend.app.engines.builder_engine import run_builder
from backend.app.engines.execution_engine import run_execution
from backend.app.engines.money_engine import run_money
from backend.app.engines.research_engine import run_research
from backend.app.engines.school_engine import run_school
from backend.app.engines.cognitive_engine import run_cognitive
from backend.app.engines.genius_engine import run_genius

def run_command(command: str):
    command = command.lower()

    if command == "money":
        return run_money("manual")

    if command == "content":
        return run_builder("manual")

    if command == "execute":
        return run_execution("manual")

    if command == "research":
        return run_research("AI systems")

    if command == "school":
        return run_school("business")

    if command == "cognitive":
        return run_cognitive()

    if command == "genius":
        return run_genius("global problem solving")

    return {"status": "unknown_command"}
