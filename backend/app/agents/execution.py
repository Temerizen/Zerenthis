from backend.core.ai import generate_text

SYSTEM = "You are the Execution agent. Turn plans and research into concrete outputs."

def run(msg: str, memory=None, knowledge=None) -> str:
    memory = memory or {}
    knowledge = knowledge or []
    return generate_text(SYSTEM, f"User memory: {memory}\n\nRelevant knowledge: {knowledge}\n\nExecution target: {msg}")

