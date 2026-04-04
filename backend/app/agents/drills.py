from backend.ai_engine import generate_text

def generate_drill(type="logic", difficulty="medium"):
    prompt = f'''
Create a {difficulty} {type} cognitive training exercise.

Return:
- question
- answer
- explanation

Keep it challenging but solvable.
'''
    return generate_text(prompt)
