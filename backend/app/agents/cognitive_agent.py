from backend.schemas.agent_response import AgentResponse
from backend.utils.formatter import format_agent_output

AGENT_NAME = "cognitive"

def run(prompt: str, context: str = "") -> AgentResponse:
    body = f"""SemantiqAI Cognitive Agent activated.

Goal:
Help improve problem solving, reasoning, focus, and thinking quality.

User Prompt:
{prompt}

Cognitive Mode:
- identify mental bottlenecks
- sharpen reasoning
- improve clarity and retention
- suggest mental drills or frameworks

Context:
{context or "No additional context"}"""

    return AgentResponse(
        agent=AGENT_NAME,
        prompt=prompt,
        output=format_agent_output(AGENT_NAME, body),
        metadata={"mode": "cognitive"}
    )
