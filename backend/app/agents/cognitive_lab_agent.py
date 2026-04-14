from backend.schemas.agent_response import AgentResponse
from backend.utils.formatter import format_agent_output

AGENT_NAME = "cognitive_lab"

def run(prompt: str, context: str = "") -> AgentResponse:
    body = f"""SemantiqAI Cognitive Lab Agent activated.

Goal:
Improve reasoning, focus, retention, problem solving, and training quality.

User Prompt:
{prompt}

Cognitive Lab Mode:
- diagnose bottlenecks
- create drills
- map improvement loops
- sharpen thinking through repetition and review

Context:
{context or "No additional context"}"""

    return AgentResponse(
        agent=AGENT_NAME,
        prompt=prompt,
        output=format_agent_output(AGENT_NAME, body),
        metadata={"mode": "cognitive_lab"}
    )

