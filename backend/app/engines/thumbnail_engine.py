from backend.ai_engine import generate_text

def generate_thumbnail_prompt(topic):
    prompt = f"""
Create a HIGH CTR YouTube thumbnail concept.

Topic: {topic}

Include:
- Visual description
- Text on thumbnail (3-5 words max)
- Emotion trigger
- Color style
- Composition

Make it irresistible.
"""
    return generate_text(prompt)

