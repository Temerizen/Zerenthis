from backend.core.ai import complete
from backend.core.agent_registry import AGENTS

def run(message: str) -> str:
    prompt = (
        message
        + "\n\nReturn:\n1. Core question\n2. Best framing\n3. Major perspectives\n4. Practical meaning\n5. Reflective next step"
    )
    return complete(AGENTS["philosophy"]["system"], prompt)

