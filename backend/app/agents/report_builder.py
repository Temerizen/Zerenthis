def build_cognitive_report(goal: str, current_state: str, target_state: str) -> dict:
    return {
        "title": f"Cognitive report | {goal}",
        "summary": f"This report maps the move from {current_state} toward {target_state}.",
        "upgrades": [
            "Increase deliberate practice frequency",
            "Improve recall instead of passive rereading",
            "Use tighter feedback loops",
            "Reduce distraction during deep work windows",
            "Track errors and convert them into drills"
        ],
        "focus_protocol": [
            "Single-task with timer",
            "Short review after each effort block",
            "Capture mistakes immediately",
            "Revisit hard material after delay"
        ]
    }

def render_cognitive_report(data: dict) -> str:
    upgrades = "\n".join([f"- {x}" for x in data["upgrades"]])
    protocol = "\n".join([f"- {x}" for x in data["focus_protocol"]])

    return f"""# {data['title']}

## Summary
{data['summary']}

## Upgrade Areas
{upgrades}

## Focus Protocol
{protocol}
"""

