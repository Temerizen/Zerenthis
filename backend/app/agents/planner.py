def normalize_subject(subject: str) -> str:
    return (subject or "").strip().lower().replace(" ", "_")

def normalize_level(level: str) -> str:
    return (level or "").strip().lower().replace(" ", "_")

def build_learning_path(subject: str, level: str) -> list[str]:
    subject = subject.strip()
    level = level.strip()

    return [
        f"Foundation map for {subject}",
        f"Core principles of {subject}",
        f"Important vocabulary and mental models in {subject}",
        f"Guided practice path for {level} learners",
        f"Error correction loops for {subject}",
        f"Testing and assessment ladder for {subject}",
        f"Real world application layer for {subject}",
        f"Mastery reinforcement system for {subject}"
    ]
