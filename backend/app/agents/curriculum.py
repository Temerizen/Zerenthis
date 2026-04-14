from backend.ai_engine import generate_text

def build_curriculum(subject: str, level: str = "beginner", goal: str = ""):
    prompt = f'''
Create a structured curriculum for:
Subject: {subject}
Level: {level}
Goal: {goal}

Return a clean learning plan with:
- course title
- course summary
- 8 to 12 modules
- each module with 3 lessons
- milestone checkpoints
- final mastery outcome

Keep it practical, rigorous, and well-ordered.
'''
    return generate_text(prompt, temperature=0.7, max_tokens=1800)

