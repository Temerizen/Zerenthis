def build_lesson(subject: str, level: str, topic: str) -> dict:
    return {
        "title": f"{subject} | {topic} | {level} lesson",
        "overview": f"This lesson teaches {topic} within {subject} at the {level} level.",
        "objectives": [
            f"Understand the core concept of {topic}",
            f"Explain {topic} clearly",
            f"Apply {topic} to problems or decisions",
            f"Recognize common mistakes in {topic}"
        ],
        "sections": [
            f"What {topic} is",
            f"Why {topic} matters",
            f"How {topic} works",
            f"When to use {topic}",
            f"Pitfalls and misconceptions in {topic}",
            f"Practice prompts for {topic}"
        ],
        "challenge": f"Teach {topic} back in your own words and solve one realistic problem involving it."
    }

def render_lesson_markdown(data: dict) -> str:
    objectives = "\n".join([f"- {x}" for x in data["objectives"]])
    sections = "\n".join([f"## {x}\nExpand this section with clear explanation and examples.\n" for x in data["sections"]])

    return f"""# {data['title']}

## Overview
{data['overview']}

## Objectives
{objectives}

{sections}

## Challenge
{data['challenge']}
"""
