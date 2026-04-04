from backend.schemas.agent_response import AgentResponse
from backend.utils.formatter import format_agent_output

AGENT_NAME = "strategy"

def run(prompt: str, context: str = "") -> AgentResponse:
    body = f"""SemantiqAI Strategy Agent activated.

Goal:
Turn a broad ambition into a sequence of intelligent moves.

User Prompt:
{prompt}

Strategy Mode:
- identify objective
- break into phases
- find constraints
- prioritize highest leverage actions

Context:
{context or "No additional context"}"""

    return AgentResponse(
        agent=AGENT_NAME,
        prompt=prompt,
        output=format_agent_output(AGENT_NAME, body),
        metadata={"mode": "strategy"}
    )
