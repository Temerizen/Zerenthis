from backend.ai_engine import generate_text

def founder_ip_system(idea):
    prompt = f'''
Create a monetizable IP system:

Idea: {idea}

Return:
- brand name
- content ecosystem
- monetization strategy
- expansion roadmap
- audience strategy

Make it scalable and powerful.
'''
    return generate_text(prompt)
