from backend.core.ai import complete
from backend.core.agent_registry import AGENTS

def run(message: str) -> str:
    prompt = (
        message
        + "\n\nReturn:\n1. Housing situation read\n2. Best path\n3. Options and tradeoffs\n4. Checklist\n5. Immediate next action"
    )
    return complete(AGENTS["housing"]["system"], prompt)
