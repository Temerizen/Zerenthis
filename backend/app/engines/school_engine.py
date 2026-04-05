from backend.app.core.output_engine import format_output

def run_school(topic):
    return format_output(
        title=f"Learn {topic}",
        summary="Structured lesson designed to teach any subject quickly and effectively.",
        steps=[
            "Explain fundamentals simply",
            "Give real examples",
            "Add exercises",
            "Test understanding"
        ],
        monetization="Sell courses or gated learning content"
    )
