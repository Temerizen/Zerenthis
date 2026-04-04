from backend.core.ai import complete
from backend.core.agent_registry import AGENTS

def run(message: str) -> str:
    prompt = (
        message
        + "\n\nReturn:\n1. Dynamic read\n2. Communication strategy\n3. Boundary guidance\n4. De-escalation move\n5. Immediate next action"
    )
    return complete(AGENTS["family"]["system"], prompt)
