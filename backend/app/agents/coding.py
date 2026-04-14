from backend.core.ai import generate_text

SYSTEM = "You are the Coding agent for SemantiqAI."

def run(msg: str, memory=None, knowledge=None) -> str:
    memory = memory or {}
    knowledge = knowledge or []
    return generate_text(SYSTEM, f"User memory: {memory}\n\nRelevant knowledge: {knowledge}\n\nCoding request: {msg}")


