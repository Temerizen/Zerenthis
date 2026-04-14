from backend.core.ai import complete
from backend.core.agent_registry import AGENTS

def run(message: str) -> str:
    prompt = (
        message
        + "\n\nReturn:\n1. Hobby fit\n2. Learning path\n3. Beginner setup\n4. Fun progression\n5. Immediate next action"
    )
    return complete(AGENTS["hobbies"]["system"], prompt)

