from backend.core.ai import generate_text

SYSTEM = "You are the Brand agent. Create positioning, messaging, voice, identity direction, and differentiation."

def run(msg: str, memory=None, knowledge=None) -> str:
    memory = memory or {}
    knowledge = knowledge or []
    return generate_text(SYSTEM, f"User memory: {memory}\n\nRelevant knowledge: {knowledge}\n\nBrand request: {msg}")

