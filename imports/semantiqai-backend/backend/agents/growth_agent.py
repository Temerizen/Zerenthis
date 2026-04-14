from backend.schemas.agent_response import AgentResponse
from backend.utils.formatter import format_agent_output

AGENT_NAME = "growth"

def run(prompt: str, context: str = "") -> AgentResponse:
    body = f"""SemantiqAI Growth Agent activated.

Goal:
Create systems for audience growth, traction, and repeatable execution.

User Prompt:
{prompt}

Growth Mode:
- define target
- create cadence
- map channels
- improve feedback loops

Context:
{context or "No additional context"}"""

    return AgentResponse(
        agent=AGENT_NAME,
        prompt=prompt,
        output=format_agent_output(AGENT_NAME, body),
        metadata={"mode": "growth"}
    )
