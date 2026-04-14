from backend.ai_engine import generate_text

def build_founder_course(subject: str, audience: str = "", monetization_goal: str = ""):
    prompt = f'''
Create a premium founder-grade course package.

Subject: {subject}
Audience: {audience}
Monetization goal: {monetization_goal}

Return:
- course name
- promise / transformation
- module breakdown
- lesson titles
- worksheet ideas
- bonus materials
- pricing angle
- landing page bullets
- upsell ideas

Make it premium and commercially strong.
'''
    return generate_text(prompt, temperature=0.8, max_tokens=2000)
