from backend.ai_engine import generate_text

def strategic_analysis(situation):
    prompt = f'''
Provide a strategic analysis.

Situation: {situation}

Return:
- key variables
- leverage points
- hidden risks
- strategic moves
- optimal path

Think like a high-level strategist.
'''
    return generate_text(prompt)

