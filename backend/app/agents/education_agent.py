from backend.schemas.agent_response import AgentResponse
from backend.utils.formatter import format_agent_output

AGENT_NAME = "education"

def run(prompt: str, context: str = "") -> AgentResponse:
    body = f"""SemantiqAI Education Agent activated.

Goal:
Teach any subject from beginner through world class level.

User Prompt:
{prompt}

Education Mode:
- map the subject clearly
- teach in levels
- build lessons, drills, and assessments
- move from confusion to mastery

Context:
{context or "No additional context"}"""

    return AgentResponse(
        agent=AGENT_NAME,
        prompt=prompt,
        output=format_agent_output(AGENT_NAME, body),
        metadata={"mode": "education_system"}
    )

