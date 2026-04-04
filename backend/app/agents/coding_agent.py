from backend.schemas.agent_response import AgentResponse
from backend.utils.formatter import format_agent_output

AGENT_NAME = "coding"

def run(prompt: str, context: str = "") -> AgentResponse:
    body = f"""SemantiqAI Coding Agent activated.

Goal:
Help build, debug, structure, and improve code systems.

User Prompt:
{prompt}

Coding Mode:
- identify implementation path
- break into modules
- keep architecture clean
- focus on usable outputs

Context:
{context or "No additional context"}"""

    return AgentResponse(
        agent=AGENT_NAME,
        prompt=prompt,
        output=format_agent_output(AGENT_NAME, body),
        metadata={"mode": "coding"}
    )
