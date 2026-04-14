from backend.ai_engine import generate_text

def generate_movie(concept):
    prompt = f'''
Create a movie concept:

Concept: {concept}

Return:
- title
- genre
- plot summary
- main characters
- 3 act structure
'''
    return generate_text(prompt)

