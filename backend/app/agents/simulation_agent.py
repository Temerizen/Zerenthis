from backend.schemas.agent_response import AgentResponse
from backend.utils.formatter import format_agent_output

AGENT_NAME = "simulation"

def run(prompt: str, context: str = "") -> AgentResponse:
    body = f"""SemantiqAI Simulation Agent activated.

Goal:
Explore scenarios, test pathways, and map possible outcomes.

User Prompt:
{prompt}

Simulation Mode:
- model paths
- identify risks
- compare outcomes
- recommend next moves

Context:
{context or "No additional context"}"""

    return AgentResponse(
        agent=AGENT_NAME,
        prompt=prompt,
        output=format_agent_output(AGENT_NAME, body),
        metadata={"mode": "simulation"}
    )

