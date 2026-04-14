from backend.dispatcher import dispatch
from backend.ai_engine import generate_text

def run_agents(message):
    agents = dispatch(message)
    outputs = []

    for a in agents:
        result = generate_text(f"[{a.upper()}]\\n" + message)
        outputs.append((a, result))

    final = "\\n\\n".join([f"[{a}]\\n{r}" for a,r in outputs])
    return final


