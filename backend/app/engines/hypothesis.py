from backend.ai_engine import generate_text

def generate_hypothesis(topic):
    prompt = f'''
Generate research-style hypotheses for:

Topic: {topic}

Important:
- These are speculative ideas, not proven facts
- Clearly label as hypothesis
- Avoid medical or dangerous claims

Return:
- 3 hypotheses
- reasoning behind each
'''
    return generate_text(prompt)
