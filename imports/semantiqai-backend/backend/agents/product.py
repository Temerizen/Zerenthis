from backend.core.ai import generate_text

SYSTEM = "You are the Product agent. Create product concepts, product structures, scope plans, and offer packages."

def run(msg: str, memory=None, knowledge=None) -> str:
    memory = memory or {}
    knowledge = knowledge or []
    return generate_text(SYSTEM, f"User memory: {memory}\n\nRelevant knowledge: {knowledge}\n\nProduct request: {msg}")

