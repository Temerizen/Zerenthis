from backend.schemas.agent_response import AgentResponse
from backend.utils.formatter import format_agent_output

AGENT_NAME = "learning"

def run(prompt: str, context: str = "") -> AgentResponse:
    body = f"""SemantiqAI Learning Agent activated.

Goal:
Help explain, teach, simplify, and structure learning.

User Prompt:
{prompt}

Teaching Mode:
- break concepts into layers
- explain clearly
- identify next learning steps
- turn confusion into clarity

Context:
{context or "No additional context"}"""

    return AgentResponse(
        agent=AGENT_NAME,
        prompt=prompt,
        output=format_agent_output(AGENT_NAME, body),
        metadata={"mode": "education"}
    )
