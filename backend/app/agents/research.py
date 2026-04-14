from backend.core.ai import generate_text

SYSTEM = "You are the Research agent. Analyze the idea, expand possibilities, identify risks, and surface options."

def run(msg: str, memory=None, knowledge=None) -> str:
    memory = memory or {}
    knowledge = knowledge or []
    return generate_text(SYSTEM, f"User memory: {memory}\n\nRelevant knowledge: {knowledge}\n\nResearch target: {msg}")


