def format_agent_output(agent_name: str, body: str) -> str:
    return f"[{agent_name.upper()}]\n\n{body.strip()}"

