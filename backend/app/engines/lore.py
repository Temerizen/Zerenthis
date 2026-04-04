from backend.ai_engine import generate_text

def generate_lore(world):
    prompt = f'''
Expand lore for:

World: {world}

Return:
- myths
- key events
- characters
- hidden secrets
'''
    return generate_text(prompt)
