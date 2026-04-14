from backend.core.ai import generate_text

SYSTEM = "You are the Content agent. Create content systems, post ideas, scripts, and content plans."

def run(msg: str, memory=None, knowledge=None) -> str:
    memory = memory or {}
    knowledge = knowledge or []
    return generate_text(SYSTEM, f"User memory: {memory}\n\nRelevant knowledge: {knowledge}\n\nContent request: {msg}")

