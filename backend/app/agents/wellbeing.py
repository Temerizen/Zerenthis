from backend.core.ai import complete
from backend.core.agent_registry import AGENTS

def run(message: str) -> str:
    prompt = (
        message
        + "\n\nReturn:\n1. Emotional read\n2. Grounding/support ideas\n3. Reframe\n4. Gentle plan\n5. Immediate next action"
    )
    return complete(AGENTS["wellbeing"]["system"], prompt)

