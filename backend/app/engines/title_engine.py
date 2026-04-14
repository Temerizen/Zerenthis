from __future__ import annotations

import random

POWER_WORDS = [
    "Reset", "System", "Blueprint", "Method", "Framework",
    "Protocol", "Engine", "Formula", "Playbook"
]

EMOTIONS = [
    "Overwhelm", "Burnout", "Chaos", "Stuck", "Frustration"
]

OUTCOMES = [
    "Clarity", "Focus", "Control", "Momentum", "Execution"
]

def generate_title(topic: str) -> str:
    emotion = random.choice(EMOTIONS)
    outcome = random.choice(OUTCOMES)
    power = random.choice(POWER_WORDS)
    return f"The {emotion} to {outcome} {power}"


