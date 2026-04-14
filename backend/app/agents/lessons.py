from backend.ai_engine import generate_text

def generate_lesson(subject: str, topic: str, level: str = "beginner", mode: str = "standard"):
    prompt = f'''
Create a lesson for:
Subject: {subject}
Topic: {topic}
Level: {level}
Mode: {mode}

Return:
- lesson title
- explanation
- examples
- key concepts
- common mistakes
- mini recap
- 3 practice questions

Make it clear, engaging, and high quality.
'''
    return generate_text(prompt, temperature=0.7, max_tokens=1600)

