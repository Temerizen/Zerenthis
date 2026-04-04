from backend.ai_engine import generate_text

def founder_command_pack(objective: str):
    prompt = f'''
Create a founder command pack for this objective:

Objective: {objective}

Return:
- immediate moves
- hidden leverage points
- module combinations to use
- likely bottlenecks
- recommended sweep priority
- command center note

Make it strategic, concise, and founder-grade.
'''
    return generate_text(prompt, temperature=0.7, max_tokens=1400)
