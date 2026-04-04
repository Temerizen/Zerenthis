from uuid import uuid4

def interpret(prompt):
    return {
        "id": uuid4().hex,
        "title": prompt[:80],
        "kind": "autonomous_build",
        "target": "backend/app/generated/" + uuid4().hex + ".py",
        "summary": prompt,
        "priority": "high",
        "status": "approved",
        "source": "chat"
    }