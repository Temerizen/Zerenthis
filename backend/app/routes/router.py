from typing import Dict, Callable
from backend.agents import (
    learning_agent,
    business_agent,
    coding_agent,
    cognitive_agent,
    strategy_agent,
    education_agent,
    cognitive_lab_agent,
    simulation_agent,
    growth_agent
)

AGENTS: Dict[str, Callable] = {
    "learning": learning_agent.run,
    "business": business_agent.run,
    "coding": coding_agent.run,
    "cognitive": cognitive_agent.run,
    "strategy": strategy_agent.run,
    "education": education_agent.run,
    "cognitive_lab": cognitive_lab_agent.run,
    "simulation": simulation_agent.run,
    "growth": growth_agent.run,
}

KEYWORD_MAP = {
    "coding": ["code", "bug", "python", "script", "backend", "frontend", "api", "debug", "build"],
    "business": ["money", "business", "revenue", "sales", "offer", "market", "profit", "monetize"],
    "learning": ["learn", "study", "explain"],
    "education": ["teach", "education", "school", "subject", "lesson", "curriculum", "class", "medical", "medicine"],
    "cognitive_lab": ["iq", "focus", "memory", "brain", "cognitive", "smarter", "reasoning", "mental training"],
    "simulation": ["simulate", "scenario", "what if", "forecast", "model outcome", "pathway"],
    "growth": ["growth", "audience", "youtube", "traction", "content strategy", "distribution"],
    "strategy": ["plan", "strategy", "roadmap", "phase", "next", "optimize", "execution"],
    "cognitive": ["thinking", "clarity", "problem solving"]
}

def select_agent(prompt: str) -> str:
    text = (prompt or "").lower()

    for agent_name, keywords in KEYWORD_MAP.items():
        if any(word in text for word in keywords):
            return agent_name

    return "strategy"

def get_agent(agent_name: str):
    return AGENTS.get(agent_name, strategy_agent.run)

