from backend.ai_engine import generate_text

def generate_book(topic):
    prompt = f'''
Create a full book structure for:

Topic: {topic}

Return:
- title
- book summary
- 10 chapter outline
- key themes
- target audience
'''
    return generate_text(prompt)

