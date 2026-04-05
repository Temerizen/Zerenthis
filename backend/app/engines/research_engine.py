from backend.app.core.output_engine import format_output

def run_research(topic):
    return format_output(
        title=f"Deep Research: {topic}",
        summary="High-level structured research with actionable insights and future implications.",
        steps=[
            "Break topic into components",
            "Analyze current state",
            "Identify opportunities",
            "Propose next innovations"
        ],
        monetization="Turn into premium PDF or consulting insights"
    )
