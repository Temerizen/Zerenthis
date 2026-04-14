from backend.core.ai import generate_text

SYSTEM = "You are the Synthesize agent. Combine multiple outputs into one polished final deliverable."

def run(msg: str, memory=None, knowledge=None) -> str:
    memory = memory or {}
    knowledge = knowledge or []
    return generate_text(SYSTEM, f"User memory: {memory}\n\nRelevant knowledge: {knowledge}\n\nItems to synthesize: {msg}")


