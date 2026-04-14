from backend.ai_engine import generate_text

def simulate_scenario(context, decision):
    prompt = f'''
Simulate a realistic outcome.

Context: {context}
Decision: {decision}

Return:
- short-term outcome
- mid-term outcome
- long-term outcome
- best case
- worst case
- unexpected consequences

Be logical and grounded.
'''
    return generate_text(prompt)
