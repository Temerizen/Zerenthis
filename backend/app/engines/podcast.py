from backend.ai_engine import generate_text

def generate_podcast(topic):
    prompt = f'''
Create a podcast episode:

Topic: {topic}

Return:
- episode title
- intro script
- main talking points
- outro
'''
    return generate_text(prompt)

