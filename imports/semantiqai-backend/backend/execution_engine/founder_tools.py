from backend.ai_engine import generate_text

def founder_execution_strategy(goal):
    prompt = f'''
Create an elite execution strategy for:

Goal: {goal}

Include:
- leverage points
- automation opportunities
- time compression strategy
- risk mitigation
- scaling path

Make it founder-level.
'''
    return generate_text(prompt)
