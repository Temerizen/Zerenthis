from backend.schemas.agent_response import AgentResponse
from backend.utils.formatter import format_agent_output

AGENT_NAME = "business"

def run(prompt: str, context: str = "") -> AgentResponse:
    body = f"""SemantiqAI Business Agent activated.

Goal:
Help with monetization, product strategy, execution paths, growth, and leverage.

User Prompt:
{prompt}

Business Mode:
- identify leverage points
- suggest business models
- organize execution steps
- prioritize speed and clarity

Context:
{context or "No additional context"}"""

    return AgentResponse(
        agent=AGENT_NAME,
        prompt=prompt,
        output=format_agent_output(AGENT_NAME, body),
        metadata={"mode": "business"}
    )

