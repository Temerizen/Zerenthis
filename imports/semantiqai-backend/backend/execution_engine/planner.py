from backend.ai_engine import generate_text

def generate_plan(goal):
    prompt = f'''
Break down this goal into an execution plan:

Goal: {goal}

Return:
- clear objective
- step-by-step tasks
- estimated timeline
- priority order
- risks
- success criteria
'''
    return generate_text(prompt)
