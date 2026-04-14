def build_cognitive_drill(focus_area: str, difficulty: str) -> dict:
    return {
        "title": f"{focus_area} drill | {difficulty}",
        "warmup": [
            f"State the goal of this {focus_area} drill in one sentence.",
            f"List the biggest distraction to strong {focus_area}."
        ],
        "drills": [
            f"Do a 5 minute focused thinking sprint on a single {focus_area} problem.",
            f"Explain a difficult concept from memory with no notes.",
            f"Find one error in your reasoning and rewrite it better.",
            f"Compress a complex idea into three sentences."
        ],
        "reflection": [
            "What felt easy?",
            "What broke your flow?",
            "What improved between minute one and minute five?",
            "What will you repeat tomorrow?"
        ]
    }

def render_cognitive_drill(data: dict) -> str:
    warmup = "\n".join([f"- {x}" for x in data["warmup"]])
    drills = "\n".join([f"- {x}" for x in data["drills"]])
    reflection = "\n".join([f"- {x}" for x in data["reflection"]])

    return f"""# {data['title']}

## Warmup
{warmup}

## Drills
{drills}

## Reflection
{reflection}
"""

