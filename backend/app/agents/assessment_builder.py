def build_assessment(subject: str, level: str, topic: str) -> dict:
    return {
        "title": f"{subject} | {topic} | {level} assessment",
        "questions": [
            f"Define {topic} in the context of {subject}.",
            f"Why does {topic} matter?",
            f"What is a common misunderstanding about {topic}?",
            f"How would you apply {topic} in a practical situation?",
            f"What would mastery of {topic} look like?"
        ],
        "rubric": [
            "Clarity of explanation",
            "Accuracy",
            "Depth of reasoning",
            "Practical application",
            "Transfer of understanding"
        ]
    }

def render_assessment_markdown(data: dict) -> str:
    questions = "\n".join([f"{idx + 1}. {q}" for idx, q in enumerate(data["questions"])])
    rubric = "\n".join([f"- {r}" for r in data["rubric"]])

    return f"""# {data['title']}

## Questions
{questions}

## Rubric
{rubric}
"""

