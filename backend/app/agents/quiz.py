from backend.ai_engine import generate_text

def generate_quiz(subject: str, topic: str, level: str = "beginner", count: int = 5):
    prompt = f'''
Create a quiz for:
Subject: {subject}
Topic: {topic}
Level: {level}
Question count: {count}

Return:
- numbered questions
- answer key
- short explanations

Use a mix of difficulty appropriate for the level.
'''
    return generate_text(prompt, temperature=0.6, max_tokens=1400)
