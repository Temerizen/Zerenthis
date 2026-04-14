from backend.core.ai import generate_text

SYSTEM = "You are the Health and Fitness agent for SemantiqAI. Do not diagnose disease."

def run(msg: str, memory=None, knowledge=None) -> str:
    memory = memory or {}
    knowledge = knowledge or []
    return generate_text(SYSTEM, f"User memory: {memory}\n\nRelevant knowledge: {knowledge}\n\nHealth request: {msg}")


