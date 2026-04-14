from backend.app.core.codegen import generate_code

def plan(goal, memory):
    prompt = f"""
You are Zerenthis planning system evolution.

GOAL:
{goal}

RECENT MEMORY:
{memory}

Break this into 3 concrete build tasks with targets and purpose.
Return JSON list.
"""
    return generate_code(prompt)
