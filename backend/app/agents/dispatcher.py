from backend.agents_registry import AGENTS

def dispatch(message):
    msg = message.lower()
    matches = []

    for key, agent in AGENTS.items():
        score = 0
        for tag in agent['tags']:
            if tag in msg:
                score += 1
        if score > 0:
            matches.append((key, agent['priority'] + score))

    if not matches:
        return ['strategist']

    matches = sorted(matches, key=lambda x: x[1], reverse=True)
    return [m[0] for m in matches[:4]]


