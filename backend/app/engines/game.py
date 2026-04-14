from backend.ai_engine import generate_text

def generate_game(concept):
    prompt = f'''
Create a game concept:

Concept: {concept}

Return:
- game title
- gameplay mechanics
- world setting
- progression system
'''
    return generate_text(prompt)

