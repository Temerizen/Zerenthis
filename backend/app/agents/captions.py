from backend.ai_engine import generate_text

def generate_captions(topic):
    prompt = f'''
Create viral social media captions for this topic: {topic}

Return:
- TikTok caption
- Instagram caption
- YouTube description (short form)
- 10 hashtags

Make it highly engaging and click-driven.
'''
    return generate_text(prompt)

