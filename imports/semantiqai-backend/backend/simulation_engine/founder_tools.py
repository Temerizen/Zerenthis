from backend.ai_engine import generate_text

def founder_simulation(command):
    prompt = f'''
Founder-level simulation.

Command: {command}

Return:
- scenario breakdown
- possible futures
- strategic advantage points
- execution recommendation

Be elite level.
'''
    return generate_text(prompt)
