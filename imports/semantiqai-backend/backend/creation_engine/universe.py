from backend.ai_engine import generate_text

def generate_universe(theme):
    prompt = f'''
Create a fictional universe:

Theme: {theme}

Return:
- world description
- factions
- history
- conflicts
- future potential
'''
    return generate_text(prompt)
