from __future__ import annotations
import random

def inject_reflection(reply: str, intent: str) -> str:
    if not reply:
        return reply

    reflections = [
        "Wait, there's something slightly off here.",
        "Actually, let me think about that for a second.",
        "That might not be the full picture.",
        "Something about this stands out.",
        "Hold on, this connects to something deeper."
    ]

    pivots = [
        "But here's the thing:",
        "The real part is this:",
        "What actually matters here is:",
        "Where this gets interesting is:"
    ]

    # Keep it occasional so it feels natural
    if random.random() < 0.35:
        reflection = random.choice(reflections)
        pivot = random.choice(pivots)
        return f"{reflection} {pivot} {reply}"

    return reply
