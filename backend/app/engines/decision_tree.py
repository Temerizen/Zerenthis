from backend.ai_engine import generate_text

def build_decision_tree(situation):
    prompt = f'''
Create a decision tree.

Situation: {situation}

Return:
- main decision paths
- branching options
- outcomes for each branch
- recommended path

Make it structured and strategic.
'''
    return generate_text(prompt)

